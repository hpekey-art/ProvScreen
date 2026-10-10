"""Fail-closed CAMPD + ECMPS raw-data adapter, preserving provenance lineage."""
import csv, json, zipfile, hashlib, re
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd


def _read_emissions(path):
    path=Path(path)
    if path.suffix.lower()=='.zip':
        with zipfile.ZipFile(path) as z:
            for n in sorted(z.namelist()):
                if n.lower().endswith('.json') and 'emissions' in Path(n).name.lower():
                    yield n, json.loads(z.read(n))
    elif path.is_dir():
        for p in sorted(path.rglob('*.json')):
            if 'emissions' in p.name.lower():yield str(p),json.loads(p.read_text())
    else:
        yield str(path),json.loads(path.read_text())


def build(bulk_path, emissions_path, outdir, *, year, selected_units=None, stack_map=None, strict=True):
    """Build event-hour CSV. stack_map: { 'ORIS|unit': 'stackId' } explicitly supplied.
    Does not infer stack allocation or claim independent unit-level stack measurements.
    """
    out=Path(outdir)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('Output directory must be empty: '+str(out))
    out.mkdir(parents=True,exist_ok=True)
    bulk=pd.read_csv(bulk_path,dtype={'Facility ID':'string','Unit ID':'string'},low_memory=False)
    names=['Facility ID','Unit ID','Date','Hour','Operating Time','NOx Mass (lbs)','NOx Mass Measure Indicator']
    if any(x not in bulk.columns for x in names): raise ValueError('Required CAMPD fields missing')
    bulk=bulk.loc[pd.to_datetime(bulk['Date']).dt.year.eq(year)].copy()
    if selected_units:
        wanted={tuple(str(v) for v in a) for a in selected_units}
        bulk=bulk[[tuple(x) in wanted for x in bulk[['Facility ID','Unit ID']].astype(str).to_numpy()]].copy()
    if not pd.to_numeric(bulk['Hour'],errors='coerce').between(0,23).all():
        raise ValueError('Invalid CAMPD hour')
    operating=pd.to_numeric(bulk['Operating Time'],errors='coerce')
    if not operating.notna().all() or not operating.between(0,1).all():
        raise ValueError('Operating Time must be finite and within [0,1]')
    valid_indicators={'Measured','Measured and Substitute','Substitute','Calculated'}
    observed=set(bulk['NOx Mass Measure Indicator'].dropna().astype(str))
    if not observed.issubset(valid_indicators):
        raise ValueError('Unknown bulk measure indicator: '+str(sorted(observed-valid_indicators)))
    bulk['timestamp']=pd.to_datetime(bulk['Date'])+pd.to_timedelta(bulk['Hour'],unit='h')
    if bulk.duplicated(['Facility ID','Unit ID','timestamp']).any():raise ValueError('Duplicate bulk unit-hour')
    sources={}; file_log=[]; found_input=False
    for filename,d in _read_emissions(emissions_path):
        if 'hourlyOperatingData' not in d:continue
        found_input=True
        if int(d.get('year',-1))!=year:raise ValueError(f'Unexpected year in {filename}')
        oris=str(d['orisCode']);quarter=int(d['quarter'])
        if quarter not in (1,2,3,4):raise ValueError('Invalid quarter '+str(quarter))
        file_log.append({'name':filename,'oris':oris,'quarter':quarter,'records':len(d['hourlyOperatingData']),
                         'sha256':hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()})
        for h in d['hourlyOperatingData']:
            location=str(h.get('unitId') or h.get('stackPipeId') or '')
            if not location:raise ValueError('Missing ECMPS location')
            date=pd.Timestamp(h['date'])
            if date.year!=year or ((date.month-1)//3+1)!=quarter:
                raise ValueError('ECMPS quarter/date mismatch in '+filename)
            if not 0<=int(h['hour'])<=23:raise ValueError('ECMPS hour outside 0..23')
            ts=str(h['date'])+'T'+str(int(h['hour'])).zfill(2)
            key=(oris,location,ts)
            if key in sources:raise ValueError('Duplicate ECMPS location-hour '+str(key))
            nx=[v for v in h.get('derivedHourlyValueData',[]) if v.get('parameterCode')=='NOXR']
            sources[key]={'noxr_count':len(nx),'modc':str(nx[0].get('modcCode') or '') if len(nx)==1 else '', 'operating_time':h.get('operatingTime'),'source_file':filename,'source_location':location}
    if not found_input:raise ValueError('No recognized ECMPS emissions exports')
    mapping=stack_map or {}
    if not isinstance(mapping,dict) or any('|' not in str(k) or not str(v) for k,v in mapping.items()):
        raise ValueError('Invalid explicit stack map')
    events=[]; missing=[]; coverage=[]
    for (fac,unit),g in bulk.groupby(['Facility ID','Unit ID'],sort=True):
        g=g.sort_values('timestamp').reset_index(drop=True)
        op=pd.to_numeric(g['Operating Time'],errors='coerce')
        for i in range(1,len(g)):
            if not (op.iloc[i]>0 and op.iloc[i-1]==0 and g.at[i,'timestamp']-g.at[i-1,'timestamp']==pd.Timedelta(hours=1)):continue
            onset=g.at[i,'timestamp']
            for offset in range(3):
                j=i+offset
                if j>=len(g) or g.at[j,'timestamp']!=onset+pd.Timedelta(hours=offset) or not op.iloc[j]>0:break
                row=g.iloc[j]; location=mapping.get(f'{fac}|{unit}',str(unit))
                ts=row['timestamp'].strftime('%Y-%m-%dT%H');source=sources.get((str(fac),str(location),ts))
                if source is None or source['noxr_count']!=1 or not source['modc']:
                    missing.append({'facility':str(fac),'unit':str(unit),'timestamp':ts,'reason':'missing_or_ambiguous_NOXR'})
                    continue
                if location==str(unit) and abs(float(source['operating_time'])-float(row['Operating Time']))>1e-9:
                    raise ValueError('Operating time discrepancy '+str((fac,unit,ts)))
                mass=row['NOx Mass (lbs)'];indicator=row['NOx Mass Measure Indicator']
                if pd.isna(mass) or pd.isna(indicator):missing.append({'facility':str(fac),'unit':str(unit),'timestamp':ts,'reason':'missing_bulk_mass_or_indicator'});continue
                events.append({'event_id':f'{fac}|{unit}|{onset.isoformat()}','facility':str(fac),'unit':str(unit),'onset':onset.isoformat(),'offset':offset,'timestamp':row['timestamp'].isoformat(),'modc':source['modc'],'noxr_count':1,'mass_A':float(mass),'bulk_indicator':str(indicator),'source_location':str(location),'provenance_type':'direct' if str(location)==str(unit) else 'shared_stack_inherited','source_file':source['source_file']})
    if strict and missing:raise ValueError(f'{len(missing)} event-hours lack unambiguous source')
    df=pd.DataFrame(events)
    df.to_csv(out/'event_hours_raw.csv',index=False) if not df.empty else pd.DataFrame(columns=['event_id','facility','unit','onset','offset','timestamp','modc','noxr_count','mass_A','bulk_indicator','source_location','provenance_type','source_file']).to_csv(out/'event_hours_raw.csv',index=False)
    pd.DataFrame(missing,columns=['facility','unit','timestamp','reason']).to_csv(out/'unresolved_hours.csv',index=False)
    pd.DataFrame(file_log).to_csv(out/'source_manifest.csv',index=False)
    report={'status':'PASS' if not missing else 'INCOMPLETE','year':year,'events':int(df.event_id.nunique()) if not df.empty else 0,'event_hours':len(df),'unresolved_hours':len(missing),'ecmps_files':len(file_log),'scope':'CAMPD unit mass; ECMPS parameter-specific NOXR; shared stack requires separate allocation audit','coverage_complete':not bool(missing),'raw_bulk_sha256':hashlib.sha256(Path(bulk_path).read_bytes()).hexdigest()}
    (out/'raw_report.json').write_text(json.dumps(report,indent=2))
    return report
