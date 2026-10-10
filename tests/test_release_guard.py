import json,subprocess,sys,tempfile,unittest
from pathlib import Path
import pandas as pd
from provscreen.engine import run
from provscreen.raw import build

class PublicationSafety(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
        self.source=Path(__file__).resolve().parents[1]/'data/ma_2024_event_hours.csv'
    def test_overwrite_prevented(self):
        dest=self.root/'result';run(self.source,dest,'frozen_2023')
        with self.assertRaises(FileExistsError):run(self.source,dest,'frozen_2023')
    def test_noncontiguous_event_rejected(self):
        d=pd.read_csv(self.source).iloc[:3].copy();d=d.iloc[[0,2]].copy()
        d.loc[:,'event_id']='test';d.loc[:,'onset']=d.iloc[0].onset
        d.loc[:,'offset']=[0,2];d.loc[:,'timestamp']=pd.to_datetime(d['onset'])+pd.to_timedelta(d['offset'],unit='h')
        f=self.root/'gap.csv';d.to_csv(f,index=False)
        with self.assertRaisesRegex(ValueError,'Noncontiguous'):run(f,self.root/'output','frozen_2023')
    def test_unknown_indicator_rejected(self):
        d=pd.read_csv(self.source).iloc[:1].copy();d.loc[:,'bulk_indicator']='TypoMeasured'
        f=self.root/'bad.csv';d.to_csv(f,index=False)
        with self.assertRaisesRegex(ValueError,'Unknown bulk indicator'):run(f,self.root/'output','frozen_2023')
    def test_atomic_cli_no_stale_output(self):
        out=self.root/'existing';out.mkdir();(out/'event_hours_raw.csv').write_text('garbage')
        result=subprocess.run([sys.executable,'-m','provscreen.cli','--source',str(self.source),'--outdir',str(out)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((out/'event_hours_raw.csv').read_text(),'garbage')
    def test_atomic_cli_good_prepared(self):
        out=self.root/'fresh'
        result=subprocess.run([sys.executable,'-m','provscreen.cli','--source',str(self.source),'--outdir',str(out)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads((out/'policy'/'report.json').read_text())['events'],829)
    def test_legal_calculated_indicator(self):
        report=run(self.source,self.root/'ok','frozen_2023')
        self.assertAlmostEqual(report['policy_mass_lbs']['B'],17305.222,places=2)
