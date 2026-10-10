#!/usr/bin/env python3
"""Reference-free portability gate for already reconstructed event-hour records.
Not a raw ECMPS ingestion engine. Supports any year/roster in audit schema.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import pandas as pd
CLASSIFIERS={'frozen_2023':{'01':'non_sub','14':'non_sub','11':'substitution','12':'unresolved'},'epa_informed_2024':{'01':'non_sub','14':'non_sub','11':'substitution','12':'unresolved','06':'substitution','08':'substitution','21':'adjustment'}}
REQUIRED=['event_id','facility','unit','onset','offset','timestamp','modc','noxr_count','mass_A','bulk_indicator']

def run(input_path,outdir,classifier):
    out=Path(outdir)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('Output directory must not exist: '+str(out))
    source=Path(input_path)
    if source.name=='event_hours_raw.csv' and (source.parent/'raw_report.json').exists():
        meta=json.loads((source.parent/'raw_report.json').read_text())
        if meta.get('status')!='PASS' or meta.get('unresolved_hours',0):
            raise ValueError('Incomplete raw adapter ledger must not be analyzed')
    d=pd.read_csv(input_path,dtype={'facility':'string','unit':'string','modc':'string','event_id':'string','bulk_indicator':'string'})
    missing=set(REQUIRED)-set(d.columns)
    if missing:raise ValueError('Missing required columns: '+','.join(sorted(missing)))
    if d.empty:raise ValueError('Empty input (no startup events); no policy estimates generated')
    if d[REQUIRED].isna().any().any():raise ValueError('Null required fields')
    if d.duplicated(['facility','unit','timestamp']).any():raise ValueError('Duplicate facility/unit/hour keys')
    if not d.offset.isin([0,1,2]).all():raise ValueError('Invalid offsets')
    if not d.noxr_count.eq(1).all():raise ValueError('NOXR ambiguous/missing')
    if (d.mass_A<0).any() or not np.isfinite(d.mass_A).all():raise ValueError('Invalid mass')
    d['onset_dt']=pd.to_datetime(d.onset)
    d['timestamp_dt']=pd.to_datetime(d.timestamp)
    if not ((d.timestamp_dt-d.onset_dt).dt.total_seconds()==d.offset*3600).all():raise ValueError('Timestamp and onset/offset mismatch')
    if d.groupby('event_id')[['facility','unit','onset']].nunique().gt(1).any().any():raise ValueError('Event identity inconsistent')
    if not d.groupby('event_id').offset.min().eq(0).all():raise ValueError('Event missing onset hour')
    for event_id, grp in d.groupby('event_id'):
        offsets=sorted(grp.offset.tolist())
        if offsets != list(range(len(offsets))) or len(offsets)>3:
            raise ValueError('Noncontiguous or duplicate event offsets: '+str(event_id))
    allowed={'Measured','Measured and Substitute','Substitute','Calculated'}
    invalid=set(d.bulk_indicator.astype(str))-allowed
    if invalid:raise ValueError('Unknown bulk indicator: '+str(sorted(invalid)))
    d['modc']=d.modc.str.zfill(2)
    d['class']=d.modc.map(CLASSIFIERS[classifier]).fillna('out_of_dictionary')
    d['B']=np.where(d.bulk_indicator.eq('Measured'),d.mass_A,0.)
    d['C']=np.where(d['class'].eq('non_sub'),d.mass_A,0.)
    good=d.groupby('event_id')['class'].transform(lambda v:v.eq('non_sub').all())
    d['eligible']=good
    d['D']=np.where(good,d.mass_A,0.)
    ev=d.groupby('event_id',as_index=False).agg(A=('mass_A','sum'),B=('B','sum'),C=('C','sum'),D=('D','sum'),eligible=('eligible','all'))
    overlaps=[]
    for frac in (.01,.05,.1):
        k=math.ceil(len(ev)*frac)
        sets={p:set(ev.sort_values([p,'event_id'],ascending=[False,True]).head(k).event_id) for p in 'ABC'}
        for p in 'BC':overlaps.append({'tail_percent':int(100*frac),'policy':p,'k':k,'overlap':len(sets['A']&sets[p])})
    report={'status':'PASS','scope':'event-hour engine only; NOT independent raw ECMPS transfer','classifier':classifier,'source_sha256':hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),'facilities':int(d.facility.nunique()),'units':int(d[['facility','unit']].drop_duplicates().shape[0]),'event_hours':len(d),'events':len(ev),'policy_mass_lbs':{p:round(float(ev[p].sum()),6) for p in 'ABCD'},'D_eligible_events':int(ev.eligible.sum()),'unknown_modc_hours':int(d['class'].eq('out_of_dictionary').sum())}
    o=out
    o.mkdir(parents=True,exist_ok=True)
    d[['event_id','facility','unit','timestamp','offset','source_location','provenance_type','source_file','modc','class','bulk_indicator','mass_A','B','C','D','eligible']].to_csv(o/'hour_decisions.csv',index=False) if {'source_location','provenance_type','source_file'}.issubset(d.columns) else d[['event_id','facility','unit','timestamp','offset','modc','class','bulk_indicator','mass_A','B','C','D','eligible']].to_csv(o/'hour_decisions.csv',index=False)
    ev.to_csv(o/'event_policy.csv',index=False);pd.DataFrame(overlaps).to_csv(o/'upper_tail.csv',index=False)
    d.groupby(['modc','class']).agg(hours=('event_id','size'),mass_lbs=('mass_A','sum')).reset_index().to_csv(o/'modc_summary.csv',index=False)
    (o/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--outdir',required=True);p.add_argument('--classifier',default='epa_informed_2024',choices=CLASSIFIERS);a=p.parse_args()
    print(json.dumps(run(a.source,a.outdir,a.classifier),indent=2))
