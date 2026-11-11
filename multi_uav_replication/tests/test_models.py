import unittest
from copy import deepcopy
import numpy as np
from config import Config
from communication_model import distance,rate,transmission_time,communication_energy,path_losses
from computation_model import computation_time,computation_energy
from energy_model import hover_power,horizontal_power,profile,flight,route,alert
from ls_fcm import membership,fit,tau
from load_balancing import allocate
from uav import UAV
from iot_devices import Task
from baseline_methods import minimum_count,exhaustive_assignment,balanced_counts
from objectives import constraints,p1_feasible,printed_p2,load_variance
from environment import Environment
from mneea import MNEEA
from task_generator import demand,tasks_for_slot
from bp_prediction import BP

class Models(unittest.TestCase):
    def setUp(self):self.c=Config()
    def test_distance(self):np.testing.assert_allclose(distance([[0,0,0]],[[3,4,12]]),[[13]])
    def test_db_rate_and_units(self):
        c=self.c; d=100.; lo,nlo=path_losses(d,c)
        expected=20*np.log10(4*np.pi*c.assumptions.carrier_hz*d/299792458.)
        self.assertAlmostEqual(lo,expected+c.assumptions.excess_los_db)
        self.assertGreater(rate(50,30,c),rate(500,30,c))
        self.assertAlmostEqual(float(transmission_time(8e6,d,30,c)*rate(d,30,c)),8e6)
        self.assertEqual(communication_energy(2,c),2)
    def test_computation(self):
        c=self.c;self.assertAlmostEqual(computation_time(1e8,c),.1)
        self.assertAlmostEqual(computation_energy(1e8,6e6,200,c),.01)
        c.assumptions.compute_energy_mode='literal_distance'
        self.assertAlmostEqual(computation_energy(1e8,6e6,200,c),2.)
    def test_profile_conservation(self):
        for length in (0,1,30,180,500):
            segments=profile(length,self.c)
            self.assertAlmostEqual(sum(v*dt+.5*a*dt*dt for dt,v,a in segments),length)
            self.assertTrue(all(v+a*dt<=30+1e-9 for dt,v,a in segments))
    def test_energy_integration(self):
        self.assertAlmostEqual(horizontal_power(0,0,self.c),hover_power(self.c))
        for mode in ('horizontal','up','down'):
            e,t=flight(30,mode,self.c);ee,tt=flight(30,mode,self.c,64)
            self.assertGreater(e,0);self.assertGreater(t,0);self.assertAlmostEqual(e,ee,places=5)
            self.assertEqual(flight(0,mode,self.c),(0.,0.))
    def test_membership_printed_exponent(self):
        np.testing.assert_allclose(membership([[1,2]],2),[[.8,.2]])
        np.testing.assert_allclose(membership([[0,1],[0,0]],2),[[1,0],[.5,.5]])
    def test_fcm_initial_and_reproducible(self):
        users=np.array([[0,0],[10,0],[490,500],[500,500]])
        initial=np.array([[50.,50.],[450.,450.]])
        c,u,g=fit(users,initial,self.c);cc,uu,gg=fit(users,initial,self.c)
        np.testing.assert_allclose(u.sum(1),1);np.testing.assert_allclose(c,cc)
        np.testing.assert_allclose(initial,[[50,50],[450,450]])
        self.assertLess(len(g),self.c.assumptions.fuzzy_iterations+1)
    def test_allocator_conserves_and_sorts(self):
        uavs=[UAV(j,np.array([j*250.,250.]),5e5) for j in range(3)]
        old=Task(0,np.array([0.,0.]),1e6,1e8,0,0,400);uavs[0].queue=[old]
        tasks=[Task(j,np.array([0.,0.]),1e6,1e8,300,1,1) for j in range(1,11)]
        allocate(uavs,tasks,self.c);ids=[t.id for u in uavs for t in u.queue]
        self.assertEqual(sorted(ids),list(range(11)));self.assertIn(old,uavs[0].queue)
        for u in uavs:self.assertEqual([t.slot for t in u.queue],sorted(t.slot for t in u.queue))
    def test_enumeration(self):
        for m in range(8):
            _,value=exhaustive_assignment(m,3,self.c)
            self.assertAlmostEqual(value,np.var(balanced_counts(m,3)))
        self.assertEqual(minimum_count(1e9,self.c),2)
        self.assertFalse(p1_feasible(1e9,1,self.c))
    def test_service_deadline(self):
        e=Environment(self.c);u=e.uavs[0];e.ready[u.id]=0
        u.queue=[Task(0,np.array([250.,250.]),1e6,5e7,0,0,1)]
        rr,ll=e.service(0);self.assertEqual(rr[0]['success'],1)
        self.assertEqual(len(u.queue),0);self.assertGreater(u.battery,0)
    def test_entry_exit_feedback_fixed(self):
        m=MNEEA(self.c)
        m.step(0,100,100,[],np.array([[20.,30.],[400.,400.]]))
        self.assertEqual(len(m.env.uavs),5)
        m.success=0;m.step(1,100,100,[],np.array([[20.,30.],[400.,400.]]))
        self.assertEqual(len(m.env.uavs),6);self.assertEqual(m.beta,1)
        m.step(2,1,1,[],np.array([[20.,30.]]));self.assertEqual(len(m.env.uavs),1)
        self.assertTrue(m.env.uavs[0].fixed)
    def test_replacement_and_landing(self):
        e=Environment(self.c);old=e.uavs[0]
        old.battery=alert(old.xy,0,0,self.c)
        e.replace_low(0)
        self.assertNotEqual(old.id,e.uavs[0].id);self.assertTrue(e.uavs[0].fixed)
        self.assertTrue(all(x.get('battery_after_j',0)>=0 for x in e.events))
    def test_seeded_tasks(self):
        np.testing.assert_array_equal(demand(2,self.c),demand(2,self.c))
        a=tasks_for_slot(70,0,np.random.default_rng(2),self.c)
        b=tasks_for_slot(70,0,np.random.default_rng(2),self.c)
        self.assertEqual([x.bits for x in a],[x.bits for x in b])
    def test_bp_learns_and_repeats(self):
        self.c.assumptions.bp_epochs=80
        x=np.random.default_rng(1).normal(size=(100,3));y=(3+x[:,0]*2)[:,None]
        m=BP(self.c).fit(x,y);n=BP(self.c).fit(x,y)
        self.assertLess(m.loss[-1],m.loss[0]);np.testing.assert_allclose(m.predict(x),n.predict(x))
    def test_literal_p2_index_typo(self):
        self.assertEqual(printed_p2([10,0,0]),0.)
        self.assertGreater(load_variance([10,0,0]),0.)
    def test_constraints(self):
        self.assertEqual(constraints([.1,2],[100,20],[1,10],self.c),{'C4_delay':False,'C5_landing':True})

if __name__=='__main__':unittest.main()
