"""Independent minimal reference linker. No import from ProvScreen. Synthetic only.
This tests correctness and semantic agreement, not superiority against established software.
"""
import json, tempfile
from pathlib import Path
import pandas as pd
from provscreen.raw import build

def reference_link(source_rows, unit, stack_map=None):
    """Independent tiny checker: explicitly typed dictionary, no event mathematics."""
    kinds={}
    for h in source_rows:
        has_unit=h.get('unitId') not in (None,'')
        has_stack=h.get('stackPipeId') not in (None,'')
        if has_unit==has_stack: raise ValueError('ambiguous identity')
        kind='unit' if has_unit else 'stack'
        ident=str(h['unitId'] if has_unit else h['stackPipeId'])
        key=(kind,ident,h['hour'])
        if key in kinds: raise ValueError('duplicate typed hour')
        kinds[key]=h
    mapped=stack_map is not None
    look=('stack',stack_map,1) if mapped else ('unit',unit,1)
    if look not in kinds:raise ValueError('missing typed source')
    return 'shared_stack_inherited' if mapped else 'direct'

def main():
    cases=[]
    for kind in ['unit','stack','dual']:
        for mapped in [False,True]:
            with tempfile.TemporaryDirectory() as d:
                d=Path(d)
                bulk=[{'Facility ID':'999','Unit ID':'A','Date':'2024-01-01','Hour':h,'Operating Time':int(h==1),'NOx Mass (lbs)':9 if h==1 else 0,'NOx Mass Measure Indicator':'Measured'} for h in range(3)]
                pd.DataFrame(bulk).to_csv(d/'bulk.csv',index=False)
                source=[]
                for h in range(3):
                    extra={'unitId':'A'} if kind=='unit' else {'stackPipeId':'A'} if kind=='stack' else {'unitId':'A','stackPipeId':'A'}
                    source.append(dict(date='2024-01-01',hour=h,operatingTime=int(h==1),derivedHourlyValueData=[{'parameterCode':'NOXR','modcCode':'01'}] if h==1 else [],**extra))
                (d/'Emissions scenario.json').write_text(json.dumps({'orisCode':999,'year':2024,'quarter':1,'hourlyOperatingData':source}))
                opts={'stack_map':{'999|A':'A'}} if mapped else {}
                try:r=build(d/'bulk.csv',d/'Emissions scenario.json',d/'out',year=2024,**opts); got=pd.read_csv(d/'out/event_hours_raw.csv').iloc[0]['provenance_type']
                except ValueError:got='reject'
                try:expected=reference_link(source,'A','A' if mapped else None)
                except ValueError:expected='reject'
                cases.append({'kind':kind,'mapped':mapped,'independent':expected,'provscreen':got,'agreement':expected==got})
    output={'scope':'six synthetic typed identity scenarios; independent reference linker, not external software','agreement':sum(x['agreement'] for x in cases),'total':len(cases),'cases':cases}
    (Path(__file__).resolve().parent/'reports'/'typed_reference_comparison_v023.json').write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2))
    if not all(x['agreement'] for x in cases):raise SystemExit('Comparison failed')
if __name__=='__main__':main()
