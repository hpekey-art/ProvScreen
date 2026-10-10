"""Same scientific rules, different raw-input contracts: a deliberately minimal flat workflow.
A careful validation-aware flat workflow can match ProvScreen; this is NOT a claim
of universal superiority or novel policy estimands.
"""
import json,tempfile
from pathlib import Path
import pandas as pd
from provscreen.raw import build
from provscreen.engine import run

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'reports'/'flat_workflow_comparison.json'

def inputs(root, *, remove_middle=False, fractional_source_hour=False):
    bulk=[];hours=[]
    for h,op,mass in [(0,0,0),(1,1,2),(2,1,3),(3,1,4),(4,0,0)]:
        if not (remove_middle and h==2):
            bulk.append({'Facility ID':'999','Unit ID':'A','Date':'2024-01-01','Hour':h,'Operating Time':op,'NOx Mass (lbs)':mass,'NOx Mass Measure Indicator':'Measured'})
        hours.append({'unitId':'A','date':'2024-01-01','hour':1.9 if (fractional_source_hour and h==1) else h,'operatingTime':op,'derivedHourlyValueData':[{'parameterCode':'NOXR','modcCode':'01'}] if op else []})
    pd.DataFrame(bulk).to_csv(root/'bulk.csv',index=False)
    (root/'Emissions fixture.json').write_text(json.dumps({'orisCode':999,'year':2024,'quarter':1,'hourlyOperatingData':hours}))
    return bulk,hours

def naive_flat(bulk,hours):
    """Simple hour-join that mimics truncation and coercion; fixed A-D rules retained."""
    source={int(v['hour']):v for v in hours}
    grouped={row['Hour']:row for row in bulk}
    onsets=[h for h in range(1,24) if h in grouped and h-1 in grouped and grouped[h]['Operating Time']>0 and grouped[h-1]['Operating Time']==0]
    selected=[]
    for h in onsets:
        for offset in range(3):
            r=grouped.get(h+offset)
            if r is None or r['Operating Time']==0:break
            v=source.get(h+offset)
            if not v:break
            selected.append({'event_id':f'999|A|2024-01-01T{h:02}:00:00','facility':'999','unit':'A','onset':f'2024-01-01T{h:02}:00:00','offset':offset,'timestamp':f'2024-01-01T{h+offset:02}:00:00','modc':v['derivedHourlyValueData'][0]['modcCode'],'noxr_count':1,'mass_A':r['NOx Mass (lbs)'],'bulk_indicator':'Measured'})
    return selected

def main():
    results=[]
    for name, kwargs in [('valid_three_hour',{}),('missing_middle_bulk_hour',{'remove_middle':True}),('fractional_ecmps_clock',{'fractional_source_hour':True})]:
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); bulk,hours=inputs(root,**kwargs)
            naive_rows=naive_flat(bulk,hours)
            naive_status='accepted'
            naive_mass=sum(r['mass_A'] for r in naive_rows)
            # The naive join uses the same policy but lacks source-shape/coverage validation.
            try:
                report=build(root/'bulk.csv',root/'Emissions fixture.json',root/'strict',year=2024)
                strict_status='accepted';strict_mass=pd.read_csv(root/'strict/event_hours_raw.csv')['mass_A'].sum()
            except ValueError as exc:
                strict_status='rejected';strict_mass=None
                reason=str(exc)
            results.append({'case':name,'flat_status':naive_status,'flat_A_mass_lb':naive_mass,'provscreen_status':strict_status,'provscreen_A_mass_lb':strict_mass,'provscreen_reason':reason if strict_status=='rejected' else None})
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps({'scope':'Synthetic contract illustration: comparison with intentionally naive flat join; not a benchmark against validated production systems','cases':results},indent=2))
    print(OUT.read_text())

if __name__=='__main__':main()
