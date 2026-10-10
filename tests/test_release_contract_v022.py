"""Publication-safety and provenance boundary probes for v0.2.2 candidate."""
import json,tempfile,unittest,sys
from pathlib import Path
import pandas as pd
from provscreen.raw import build
from provscreen.engine import run

class PublicationContracts(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.p=Path(self.t.name)
  self.rows=[{'Facility ID':'999','Unit ID':'A','Date':'2024-01-01','Hour':h,'Operating Time':op,'NOx Mass (lbs)':float(h),'NOx Mass Measure Indicator':'Measured'} for h,op in [(0,0),(1,1),(2,1),(3,1),(4,0)]]
  self.hours=[{'unitId':'A','date':'2024-01-01','hour':h,'operatingTime':op,'derivedHourlyValueData':([{'parameterCode':'NOXR','modcCode':'01'}] if op else [])} for h,op in [(0,0),(1,1),(2,1),(3,1),(4,0)]]
 def save(self):
  b=self.p/'bulk.csv';j=self.p/'Emissions fixture.json'
  pd.DataFrame(self.rows).to_csv(b,index=False)
  j.write_text(json.dumps({'orisCode':999,'year':2024,'quarter':1,'hourlyOperatingData':self.hours}))
  return b,j
 def test_coverage_scope_is_observed_not_annual(self):
  b,j=self.save();r=build(b,j,self.p/'raw',year=2024)
  self.assertTrue(r['source_links_complete']);self.assertFalse(r['coverage_complete'])
  coverage=pd.read_csv(self.p/'raw/coverage_manifest.csv')
  self.assertEqual(len(coverage),1);self.assertFalse(bool(coverage.calendar_year_complete.iloc[0]))
 def test_engine_rejects_partial_adapter_ledger(self):
  self.hours[2]['derivedHourlyValueData']=[]
  b,j=self.save();r=build(b,j,self.p/'raw',year=2024,strict=False)
  self.assertEqual(r['status'],'INCOMPLETE')
  with self.assertRaisesRegex(ValueError,'Incomplete raw adapter'):
   run(self.p/'raw/event_hours_raw.csv',self.p/'policy','frozen_2023')
 def test_engine_refuses_nonempty_existing_output(self):
  b,j=self.save();build(b,j,self.p/'raw',year=2024)
  o=self.p/'output';o.mkdir();(o/'old.csv').write_text('sentinel')
  with self.assertRaises(FileExistsError):run(self.p/'raw/event_hours_raw.csv',o,'frozen_2023')
  self.assertEqual((o/'old.csv').read_text(),'sentinel')
 def test_hour_decisions_have_source_and_eligibility(self):
  b,j=self.save();build(b,j,self.p/'raw',year=2024)
  run(self.p/'raw/event_hours_raw.csv',self.p/'policy','frozen_2023')
  d=pd.read_csv(self.p/'policy/hour_decisions.csv')
  self.assertEqual(len(d),3)
  self.assertTrue({'source_file','source_location','provenance_type','class','eligible','B','C','D'}.issubset(d.columns))
 def test_full_year_requires_explicit_complete_calendar(self):
  b,j=self.save()
  with self.assertRaisesRegex(ValueError,'full-year'):
   build(b,j,self.p/'raw',year=2024,require_full_year=True)
 def test_missing_declared_roster_unit_rejected(self):
  b,j=self.save()
  with self.assertRaisesRegex(ValueError,'roster mismatch'):
   build(b,j,self.p/'raw',year=2024,expected_roster=[['999','A'],['999','B']])
 def test_f28_duplicated_unit_identity_rejected(self):
  import importlib.util
  sp=importlib.util.spec_from_file_location('verify_f28',str(Path(__file__).resolve().parents[1]/'verify_f28.py'))
  module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
  src=Path(__file__).resolve().parents[1]/'evidence/F28_hourly_unit_reconciliation.csv'
  d=pd.read_csv(src);group=d[(d.date==d.date.iloc[0])&(d.hour==d.hour.iloc[0])]
  d.loc[group.index[1],'unit']=d.loc[group.index[0],'unit']
  corrupted=self.p/'bad.csv';d.to_csv(corrupted,index=False)
  with self.assertRaisesRegex(ValueError,'Duplicate unit identity'):module.verify(corrupted)
if __name__=='__main__':unittest.main()
