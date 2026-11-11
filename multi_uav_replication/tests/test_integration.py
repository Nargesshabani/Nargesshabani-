import csv
import tempfile
import unittest
from pathlib import Path
from copy import deepcopy
import numpy as np
from config import Config
from evaluation import daily
from environment import Environment
from energy_model import flight,route
from baseline_methods import greedy
from iot_devices import Task
from uav import UAV
from bp_prediction import BP

class Integration(unittest.TestCase):
    def test_daily_reproducibility_and_shared_tasks(self):
        c=Config();c.paper.slots=6
        counts=np.array([5,70,100,70,2,2]);pred=np.array([5,60,90,80,10,2])
        with tempfile.TemporaryDirectory() as first,tempfile.TemporaryDirectory() as second:
            daily(c,Path(first),counts,pred);daily(c,Path(second),counts,pred)
            for filename in ('daily_metrics.csv','task_results.csv','uav_events.csv','energy_ledger.csv','summary.csv'):
                self.assertEqual((Path(first)/filename).read_bytes(),(Path(second)/filename).read_bytes())
            with open(Path(first)/'task_results.csv') as f: rows=list(csv.DictReader(f))
            traces={}
            for r in rows: traces.setdefault(r['policy'],{})[r['task_id']]=(r['bits'],r['cycles'],r['arrival_s'])
            self.assertEqual(len(traces),4)
            for trace in traces.values(): self.assertEqual(trace,traces['proposed'])
            with open(Path(first)/'energy_ledger.csv') as f: energy=list(csv.DictReader(f))
            self.assertTrue(all(float(r['joules'])>=0 for r in energy))
    def test_literal_horizontal_failure_is_exposed(self):
        c=Config();c.assumptions.horizontal_mode='printed'
        e,t=flight(500,'horizontal',c)
        self.assertGreater(e,c.paper.battery_j)
        c.assumptions.horizontal_mode='force_balance'
        repaired,_=flight(500,'horizontal',c)
        self.assertLess(repaired,c.paper.battery_j)
    def test_greedy_available_resource_rule(self):
        c=Config();c.assumptions.deadline_s=10
        us=[UAV(0,np.array([0.,0.]),5e5),UAV(1,np.array([500.,500.]),5e5)]
        t=Task(1,np.array([490.,490.]),1e6,1e8,0,0,10)
        greedy(us,[t],c)
        self.assertEqual(us[1].queue[0].id,1)
    def test_long_idle_replacement_no_exhaustion(self):
        c=Config();c.paper.slot_s=10000
        e=Environment(c);e.ready[0]=0
        records,loads=e.service(0)
        self.assertGreater(sum(r['kind']=='replacement' for r in e.events),1)
        for u in e.uavs:self.assertGreaterEqual(u.battery,route(u.xy,c,True)[0])
        self.assertTrue(all(r.get('battery_after_j',0)>=-1e-7 for r in e.events))
    def test_model_persistence(self):
        c=Config();c.assumptions.bp_epochs=2
        x=np.arange(30).reshape(10,3);y=np.arange(10)[:,None]
        model=BP(c).fit(x,y)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'model.npz';model.save(path)
            np.testing.assert_allclose(model.predict(x),BP.load(path,c).predict(x))
