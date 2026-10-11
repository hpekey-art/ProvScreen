import json, tempfile, unittest
from pathlib import Path
import pandas as pd
from provscreen.raw import build

class TypedLineageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.bulk=self.root/'bulk.csv';self.src=self.root/'Emissions - boundary.json'
        pd.DataFrame([
            {'Facility ID':'999','Unit ID':'A','Date':'2024-01-01','Hour':0,'Operating Time':0,'NOx Mass (lbs)':0,'NOx Mass Measure Indicator':'Measured'},
            {'Facility ID':'999','Unit ID':'A','Date':'2024-01-01','Hour':1,'Operating Time':1,'NOx Mass (lbs)':9,'NOx Mass Measure Indicator':'Measured'},
            {'Facility ID':'999','Unit ID':'A','Date':'2024-01-01','Hour':2,'Operating Time':0,'NOx Mass (lbs)':0,'NOx Mass Measure Indicator':'Measured'}
        ]).to_csv(self.bulk,index=False)
    def save(self, rows):
        self.src.write_text(json.dumps({'orisCode':999,'year':2024,'quarter':1,'hourlyOperatingData':rows}))
    def hour(self, h, **kwargs):
        return dict(date='2024-01-01',hour=h,operatingTime=1 if h==1 else 0,derivedHourlyValueData=[{'parameterCode':'NOXR','modcCode':'01'}] if h==1 else [], **kwargs)
    def test_both_identity_fields_rejected(self):
        self.save([self.hour(h,unitId='A',stackPipeId='A') for h in range(3)])
        with self.assertRaisesRegex(ValueError,'exactly one'):build(self.bulk,self.src,self.root/'o',year=2024)
    def test_coincident_stack_without_map_rejected(self):
        self.save([self.hour(h,stackPipeId='A') for h in range(3)])
        with self.assertRaisesRegex(ValueError,'lack unambiguous source'):build(self.bulk,self.src,self.root/'o',year=2024)
    def test_coincident_stack_with_explicit_map_is_inherited(self):
        self.save([self.hour(h,stackPipeId='A') for h in range(3)])
        result=build(self.bulk,self.src,self.root/'o',year=2024,stack_map={'999|A':'A'})
        self.assertEqual((result['events'],result['event_hours']),(1,1))
        x=pd.read_csv(self.root/'o'/'event_hours_raw.csv')
        self.assertEqual(x.iloc[0]['provenance_type'],'shared_stack_inherited')
    def test_direct_unit_is_direct(self):
        self.save([self.hour(h,unitId='A') for h in range(3)])
        build(self.bulk,self.src,self.root/'o',year=2024)
        x=pd.read_csv(self.root/'o'/'event_hours_raw.csv')
        self.assertEqual(x.iloc[0]['provenance_type'],'direct')
    def test_distinct_unit_and_stack_labels_coexist(self):
        self.save([self.hour(h,unitId='A') for h in range(3)]+[self.hour(h,stackPipeId='A') for h in range(3)])
        build(self.bulk,self.src,self.root/'o',year=2024)
        x=pd.read_csv(self.root/'o'/'event_hours_raw.csv')
        self.assertEqual(x.iloc[0]['provenance_type'],'direct')

if __name__=='__main__':unittest.main()
