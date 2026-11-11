"""Independent output invariants; run after main.py."""
import csv,json,hashlib
from pathlib import Path

def rows(path):
    with open(path) as f:return list(csv.DictReader(f))
def validate(root):
    root=Path(root); result=root/'results'; checks={}
    metrics=rows(result/'daily_metrics.csv');tasks=rows(result/'task_results.csv')
    cfg=json.loads((result/'config.json').read_text());policies=('fixed','prediction','proposed','enumeration')
    for p in policies:
        mm=[r for r in metrics if r['policy']==p]
        assert len(mm)==cfg['paper']['slots']
        assert all(int(r['active_uavs'])>=1 for r in mm)
        tt=[r for r in tasks if r['policy']==p]
        assert len({r['task_id'] for r in tt})==len(tt)
        assert sum(int(r['completed'])+int(r['failed']) for r in mm)==len(tt)
        assert all(float(r['delay_s'])<=cfg['assumptions']['deadline_s']+1e-7 for r in tt if r['success']=='1')
    traces={p:{r['task_id']:(r['bits'],r['cycles'],r['arrival_s']) for r in tasks if r['policy']==p} for p in policies}
    assert all(t==traces['proposed'] for t in traces.values())
    checks['shared_tasks_and_outcome_conservation']=True
    ee=rows(result/'energy_ledger.csv')
    assert all(float(r['joules'])>=0 for r in ee)
    events=rows(result/'uav_events.csv')
    assert all(float(r['battery_after_j'])>=-1e-7 for r in events if r.get('battery_after_j'))
    for s in rows(result/'summary.csv'):
        total=sum(float(r['joules']) for r in ee if r['policy']==s['policy'])
        assert abs(total-float(s['energy_j']))<1e-6
    checks['energy_ledger_and_landing_reserves']=True
    for r in rows(result/'enumeration_verification.csv'):
        assert abs(float(r['exhaustive_variance'])-float(r['analytic_variance']))<1e-12
    checks['exhaustive_small_case_optimum']=True
    assert len(rows(result/'prediction.csv'))==cfg['paper']['slots']
    dataset=rows(result/'training_dataset.csv')
    train={r['day'] for r in dataset if r['split']=='train'};test={r['day'] for r in dataset if r['split']=='holdout'}
    assert not train.intersection(test)
    checks['disjoint_training_holdout_dates']=True
    for policy in ('proposed','greedy','count_optimum'):
        rr=[r for r in rows(result/'short_comparison.csv') if r['method']==policy]
        assert len(rr)==cfg['assumptions']['short_slots']*cfg['assumptions']['short_uavs']
    checks['short_comparison_dimensions']=True
    checks['csv_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(result.glob('*.csv'))}
    (result/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
    print('Validated output invariants and CSV checksums.')
if __name__=='__main__':validate(Path(__file__).parent)
