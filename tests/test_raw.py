import json, tempfile, unittest
from pathlib import Path
import pandas as pd
from provscreen.raw import build
from provscreen.engine import run

class RawAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        rows=[]; hours=[]
        for h,(op,mass,modc) in enumerate([(0,None,None),(1,2.5,'01'),(1,3.0,'11'),(0,None,None),(1,4.,'14')]):
            rows.append({'Facility ID':'999','Unit ID':'A','Date':'2024-01-01','Hour':h,'Operating Time':op,'NOx Mass (lbs)':mass,'NOx Mass Measure Indicator':'Measured'})
            hours.append({'unitId':'A','stackPipeId':None,'date':'2024-01-01','hour':h,'operatingTime':op,'derivedHourlyValueData':[] if not modc else [{'parameterCode':'NOXR','modcCode':modc}]})
        pd.DataFrame(rows).to_csv(self.root/'bulk.csv',index=False)
        (self.root/'Emissions - fixture.json').write_text(json.dumps({'orisCode':999,'year':2024,'quarter':1,'hourlyOperatingData':hours}))
    def tearDown(self):self.tmp.cleanup()
    def test_raw_end_to_end(self):
        r=build(self.root/'bulk.csv',self.root/'Emissions - fixture.json',self.root/'out',year=2024)
        self.assertEqual((r['events'],r['event_hours']),(2,3))
        v=run(self.root/'out/event_hours_raw.csv',self.root/'policy','epa_informed_2024')
        self.assertEqual(v['policy_mass_lbs']['A'],9.5)
        self.assertEqual(v['policy_mass_lbs']['C'],6.5)
        self.assertEqual(v['D_eligible_events'],1)
    def test_missing_noxr_fails_closed(self):
        p=self.root/'Emissions - fixture.json';d=json.loads(p.read_text());d['hourlyOperatingData'][1]['derivedHourlyValueData']=[];p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'lack unambiguous source'):build(self.root/'bulk.csv',p,self.root/'out',year=2024)
    def test_duplicate_source_fails(self):
        p=self.root/'Emissions - fixture.json';d=json.loads(p.read_text());d['hourlyOperatingData'].append(d['hourlyOperatingData'][1]);p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'Duplicate ECMPS'):build(self.root/'bulk.csv',p,self.root/'out',year=2024)
if __name__=='__main__':unittest.main()
