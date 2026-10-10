import csv,json,sys,unittest,tempfile
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from provscreen.engine import run

EXPECTED_RI={'events':1233,'event_hours':3568,'A':152527.348,'B':145905.497,'C':146435.058,'D':140385.959,'D_events':1125}
EXPECTED_MA={'events':829,'event_hours':1997,'A':18035.757,'B':17305.222,'C':17939.975,'D':17897.087,'D_events':813}

class Regression(unittest.TestCase):
    def check_ref(self,source,cls,ref):
        with tempfile.TemporaryDirectory() as tmp:
            result=run(str(ROOT/'data'/source),tmp,cls)
            self.assertEqual(result['events'],ref['events'])
            self.assertEqual(result['event_hours'],ref['event_hours'])
            self.assertEqual(result['D_eligible_events'],ref['D_events'])
            for k in 'ABCD':self.assertAlmostEqual(result['policy_mass_lbs'][k],ref[k],places=3)
            self.assertTrue((Path(tmp)/'upper_tail.csv').exists())
    def test_ri2024_frozen(self):self.check_ref('ri_2024_event_hours.csv','frozen_2023',EXPECTED_RI)
    def test_ri2024_epa(self):self.check_ref('ri_2024_event_hours.csv','epa_informed_2024',EXPECTED_RI)
    def test_ma2024_frozen(self):self.check_ref('ma_2024_event_hours.csv','frozen_2023',EXPECTED_MA)
    def test_ma2024_epa(self):self.check_ref('ma_2024_event_hours.csv','epa_informed_2024',EXPECTED_MA)
    def test_invalid_offset_rejected(self):
        d=pd.read_csv(ROOT/'data/ma_2024_event_hours.csv');d.loc[0,'offset']=3
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/'bad.csv';d.to_csv(src,index=False)
            with self.assertRaisesRegex(ValueError,'Invalid offsets'):run(src,Path(t)/'out','frozen_2023')
    def test_duplicate_hour_rejected(self):
        d=pd.read_csv(ROOT/'data/ma_2024_event_hours.csv');d=pd.concat([d,d.iloc[[0]]],ignore_index=True)
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/'duplicate.csv';d.to_csv(src,index=False)
            with self.assertRaisesRegex(ValueError,'Duplicate'):run(src,Path(t)/'out','frozen_2023')
    def test_mass_negative_rejected(self):
        d=pd.read_csv(ROOT/'data/ma_2024_event_hours.csv');d.loc[0,'mass_A']=-1
        with tempfile.TemporaryDirectory() as t:
            src=Path(t)/'bad.csv';d.to_csv(src,index=False)
            with self.assertRaisesRegex(ValueError,'Invalid mass'):run(src,Path(t)/'out','frozen_2023')
    def test_2023_frozen_reference(self):
        # Independent 2023 frozen event-master baseline audit; not raw ECMPS reconstruction.
        p=ROOT/'reference/2023_event_master.csv'
        d=pd.read_csv(p)
        self.assertEqual(len(d),1257)
        got={'A':d.mass_A.sum(),'B':d.mass_B.sum(),'C':d.mass_C.sum(),'D':d.loc[d.D_complete.eq(1),'mass_A'].sum()}
        expected={'A':169402.520,'B':163418.319,'C':164325.569,'D':157252.957}
        for k in got:self.assertAlmostEqual(got[k],expected[k],places=3)
        self.assertEqual(int(d.D_complete.sum()),1186)
if __name__=='__main__':unittest.main()
