"""Atomic, fail-closed command-line orchestration."""
import argparse,json,tempfile,os,hashlib,platform,sys,importlib.metadata
from pathlib import Path
from .engine import run,CLASSIFIERS

def main():
    p=argparse.ArgumentParser(description='ProvScreen: local CAMPD CSV + ECMPS emissions JSON/ZIP or validated event-hour CSV')
    p.add_argument('--source',help='Validated event-hour CSV')
    p.add_argument('--raw-bulk',help='Local CAMPD hourly CSV (not an EPA downloader)')
    p.add_argument('--ecmps',help='Local ECMPS Emissions Export JSON/ZIP/folder')
    p.add_argument('--year',type=int)
    p.add_argument('--stack-map',help='Explicit JSON ORIS|unit to shared-stack location')
    p.add_argument('--expected-roster',help='JSON list of [ORIS,unit] pairs required in CAMPD input')
    p.add_argument('--require-full-year',action='store_true',help='Fail unless every scoped unit has every clock hour of selected year')
    p.add_argument('--outdir',required=True)
    p.add_argument('--classifier',choices=sorted(CLASSIFIERS),default='epa_informed_2024')
    a=p.parse_args()
    target=Path(a.outdir).resolve()
    if target.exists():
        p.error('Output path already exists; specify a new run directory')
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.provscreen-staging-',dir=target.parent) as staging:
        if a.raw_bulk:
            if not a.ecmps or not a.year:p.error('--raw-bulk requires --ecmps and --year')
            from .raw import build
            mapping=json.loads(Path(a.stack_map).read_text()) if a.stack_map else None
            raw_dir=Path(staging)/'raw'
            roster=json.loads(Path(a.expected_roster).read_text()) if a.expected_roster else None
            raw_report=build(a.raw_bulk,a.ecmps,raw_dir,year=a.year,stack_map=mapping,expected_roster=roster,require_full_year=a.require_full_year)
            if raw_report['status']!='PASS' or not raw_report['event_hours']:
                raise ValueError('No complete nonempty raw event ledger; engine was not run')
            result=run(raw_dir/'event_hours_raw.csv',Path(staging)/'policy',a.classifier)
        elif a.source:
            result=run(a.source,Path(staging)/'policy',a.classifier)
        else:p.error('Specify --source or --raw-bulk')
        def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
        artefacts={str(q.relative_to(staging)):sha(q) for q in Path(staging).rglob('*') if q.is_file()}
        config={'mode':'raw' if a.raw_bulk else 'prepared','year':a.year,'classifier':a.classifier,'selected_units':'not exposed by CLI','stack_map_sha256':sha(a.stack_map) if a.stack_map else None,'expected_roster_sha256':sha(a.expected_roster) if a.expected_roster else None,'require_full_year':a.require_full_year,'input_bulk_sha256':sha(a.raw_bulk) if a.raw_bulk else None,'input_prepared_sha256':sha(a.source) if a.source else None,'input_ecmps_path':str(a.ecmps) if a.ecmps else None,'python':sys.version.split()[0],'platform':platform.platform(),'package_version':importlib.metadata.version('provscreen-noxtools') if importlib.metadata.packages_distributions().get('provscreen') else 'local-source','outputs_sha256':artefacts}
        (Path(staging)/'run_manifest.json').write_text(json.dumps(config,indent=2,sort_keys=True),encoding='utf-8')
        os.rename(staging,target)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
