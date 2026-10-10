"""Atomic, fail-closed command-line orchestration."""
import argparse,json,tempfile,os
from pathlib import Path
from .engine import run,CLASSIFIERS

def main():
    p=argparse.ArgumentParser(description='ProvScreen: local CAMPD CSV + ECMPS emissions JSON/ZIP or validated event-hour CSV')
    p.add_argument('--source',help='Validated event-hour CSV')
    p.add_argument('--raw-bulk',help='Local CAMPD hourly CSV (not an EPA downloader)')
    p.add_argument('--ecmps',help='Local ECMPS Emissions Export JSON/ZIP/folder')
    p.add_argument('--year',type=int)
    p.add_argument('--stack-map',help='Explicit JSON ORIS|unit to shared-stack location')
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
            raw_report=build(a.raw_bulk,a.ecmps,raw_dir,year=a.year,stack_map=mapping)
            if raw_report['status']!='PASS' or not raw_report['event_hours']:
                raise ValueError('No complete nonempty raw event ledger; engine was not run')
            result=run(raw_dir/'event_hours_raw.csv',Path(staging)/'policy',a.classifier)
        elif a.source:
            result=run(a.source,Path(staging)/'policy',a.classifier)
        else:p.error('Specify --source or --raw-bulk')
        os.rename(staging,target)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
