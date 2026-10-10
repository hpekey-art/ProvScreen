"""Regression fixtures for reproduced S01/S02 vulnerabilities; no scientific rule changes."""
import json, tempfile, unittest
from pathlib import Path
import pandas as pd
from provscreen.raw import build
from provscreen.engine import run

class CriticalRawContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)
        self.bulk=[];self.hours=[]
        # Onset at 01:00, followed by 02:00 and 03:00; explicit zeros bookend it.
        for hour, op, mass in [(0,0,0),(1,1,2),(2,1,3),(3,1,4),(4,0,0)]:
            self.bulk.append({'Facility ID':'999','Unit ID':'A','Date':'2024-01-01','Hour':hour,'Operating Time':op,'NOx Mass (lbs)':mass,'NOx Mass Measure Indicator':'Measured'})
            self.hours.append({'unitId':'A','date':'2024-01-01','hour':hour,'operatingTime':op,'derivedHourlyValueData':([{'parameterCode':'NOXR','modcCode':'01'}] if op else [])})
    def save(self):
        b=self.p/'bulk.csv';j=self.p/'Emissions fixture.json'
        pd.DataFrame(self.bulk).to_csv(b,index=False)
        j.write_text(json.dumps({'orisCode':999,'year':2024,'quarter':1,'hourlyOperatingData':self.hours}))
        return b,j
    def test_valid_three_hours_still_nine_pounds(self):
        b,j=self.save();r=build(b,j,self.p/'raw',year=2024)
        self.assertEqual((r['events'],r['event_hours']),(1,3))
        result=run(self.p/'raw/event_hours_raw.csv',self.p/'policy','frozen_2023')
        self.assertEqual(result['policy_mass_lbs']['D'],9.)
    def test_missing_middle_bulk_hour_rejected(self):
        self.bulk=[row for row in self.bulk if row['Hour']!=2]
        b,j=self.save()
        with self.assertRaisesRegex(ValueError,'coverage gap'): build(b,j,self.p/'raw',year=2024)
    def test_legitimate_explicit_zero_ends_event(self):
        self.bulk[2]['Operating Time']=0;self.hours[2]['operatingTime']=0
        b,j=self.save();r=build(b,j,self.p/'raw',year=2024)
        self.assertEqual((r['events'],r['event_hours']),(2,2))
    def test_fractional_ecmps_hour_rejected(self):
        self.hours[1]['hour']=1.9
        b,j=self.save()
        with self.assertRaisesRegex(ValueError,'Invalid ECMPS hour'):build(b,j,self.p/'raw',year=2024)
    def test_ecmps_nan_op_rejected(self):
        self.hours[1]['operatingTime']=float('nan')
        b,j=self.save()
        with self.assertRaisesRegex(ValueError,'Invalid ECMPS source Operating Time'):build(b,j,self.p/'raw',year=2024)
    def test_ecmps_op_out_of_range_rejected(self):
        self.hours[1]['operatingTime']=1.5
        b,j=self.save()
        with self.assertRaisesRegex(ValueError,'Invalid ECMPS source Operating Time'):build(b,j,self.p/'raw',year=2024)
    def test_fractional_bulk_hour_rejected(self):
        self.bulk[1]['Hour']=1.9
        b,j=self.save()
        with self.assertRaisesRegex(ValueError,'Invalid CAMPD hour'):build(b,j,self.p/'raw',year=2024)
    def test_shared_stack_invalid_operating_time_rejected(self):
        for r in self.hours:
            r.pop('unitId',None)
            r['stackPipeId']='CS2'
        self.hours[1]['operatingTime']=1.5
        b,j=self.save()
        with self.assertRaisesRegex(ValueError,'Invalid ECMPS source Operating Time'):
            build(b,j,self.p/'raw',year=2024,stack_map={'999|A':'CS2'})
    def test_legitimate_stack_op_differs_from_unit(self):
        for r in self.hours:
            r.pop('unitId',None)
            r['stackPipeId']='CS2'
        # Shared-stack operating time need not equal unit operating time.
        self.hours[1]['operatingTime']=0.5
        b,j=self.save()
        self.assertEqual(build(b,j,self.p/'raw',year=2024,stack_map={'999|A':'CS2'})['event_hours'],3)
    def test_misidentified_stack_rejected(self):
        b,j=self.save()
        # Reuse a second unit-type location as the alleged stack source.
        for r in self.hours:r['unitId']='B'
        b,j=self.save()
        with self.assertRaisesRegex(ValueError,'must be a stackPipeId'):build(b,j,self.p/'raw',year=2024,stack_map={'999|A':'B'})

if __name__=='__main__':unittest.main()
