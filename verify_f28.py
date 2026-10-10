"""Check supplied F28 reconciliation ledger without altering upstream science."""
from pathlib import Path
import argparse,json,hashlib
import pandas as pd
import numpy as np

def verify(csv_path, tol=0.001):
    path=Path(csv_path)
    d=pd.read_csv(path)
    required={'unit','active_units','CS2_NOX_rate','CS2_operating_time','F28_share','predicted_unit_mass_lb','CAMPD_unit_mass_lb','difference_lb'}
    if not required.issubset(d):raise ValueError('Missing reconciliation columns: '+str(required-set(d)))
    if len(d)!=7120:raise ValueError('Unexpected reconciliation scope; expected 7120 unit-hours')
    expected=d.CS2_NOX_rate*d.CS2_operating_time*d.F28_share
    if not np.allclose(expected,d.predicted_unit_mass_lb,rtol=0,atol=1e-9):raise ValueError('Arithmetic reconciliation failed')
    delta=d.predicted_unit_mass_lb-d.CAMPD_unit_mass_lb
    if not np.allclose(delta,d.difference_lb,rtol=0,atol=1e-9):raise ValueError('Difference ledger mismatch')
    maximum=float(delta.abs().max())
    if maximum>tol:raise ValueError('Allocation disagreement exceeds tolerance')
    groups=d.groupby(['date','hour']); active=groups.active_units.first()
    if not ((groups.size()==2).all() and (active.isin([1,2])).all()):raise ValueError('Unexpected stack pairing')
    if not np.allclose(groups.F28_share.sum(),1,rtol=0,atol=1e-9):raise ValueError('Shares do not sum to 1')
    if not set(d.unit.astype(str)).issubset({'11','12'}):raise ValueError('Unexpected unit identity')
    for (_, _),group in groups:
        active_rows=group[group.F28_share>1e-12]
        if len(active_rows)!=int(group.active_units.iloc[0]):raise ValueError('Active-unit count differs from positive shares')
        if len(set(group.unit.astype(str)))!=len(group):raise ValueError('Duplicate unit identity in stack hour')
        if not group.active_units.eq(group.active_units.iloc[0]).all():raise ValueError('Inconsistent active units')
        # Inactive unit can have an undefined HI rate; its contribution is exactly zero.
        if not group.unit_operating_time.between(0,1).all():raise ValueError('Invalid unit operating time')
        if not np.isfinite(group.loc[group.unit_operating_time>0,'unit_HI_rate']).all():raise ValueError('Active unit heat input missing')
        factors=(group.unit_HI_rate.fillna(0)*group.unit_operating_time)
        if not np.isfinite(factors).all() or (factors<0).any() or factors.sum()<=0:raise ValueError('Invalid heat-input weights')
        shares=factors/factors.sum()
        if not np.allclose(shares,group.F28_share,rtol=0,atol=1e-9):raise ValueError('F28 heat-input share mismatch')
    return {'status':'PASS','rows':len(d),'max_abs_difference_lb':maximum,'sum_difference_lb':float(delta.sum()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Supplied F28 ledger; not independently recreated from regulatory raw source'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('ledger');ap.add_argument('--output'); a=ap.parse_args()
    result=verify(a.ledger)
    if a.output:Path(a.output).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
