"""Algorithm 2 in printed order, with documented pseudocode repairs."""
import numpy as np
from environment import Environment
from load_balancing import allocate
from baseline_methods import minimum_count,greedy

class MNEEA:
    def __init__(self,cfg,policy='proposed'):
        self.cfg=cfg; self.env=Environment(cfg); self.policy=policy
        self.beta=0; self.previous_count=None; self.success=1.
    def add(self,time):
        a=self.cfg.assumptions; n=len(self.env.uavs)
        if n>=a.max_uavs: raise RuntimeError('max_uavs reached')
        angle=n*2.399963229728653
        xy=np.clip(np.array(a.base_xy)+a.initial_mobile_radius_m*np.array([np.cos(angle),np.sin(angle)]),0,self.cfg.paper.area_m)
        self.env.launch(xy,time)
    def step(self,slot,count,predicted_count,tasks,positions):
        c=self.cfg; t=slot*c.paper.slot_s; e=self.env
        e.replace_low(t); alpha=0
        if count!=self.previous_count: self.beta=0
        need=max(0,predicted_count)*np.mean(c.paper.cycles)*c.assumptions.arrival_probability
        if self.policy=='fixed':
            target=c.assumptions.fixed_uavs
        elif self.policy=='enumeration':
            target=minimum_count(sum(x.cycles for x in tasks),c)
        else:
            target=None
            while need/(len(e.uavs)*c.paper.cpu_hz)>c.assumptions.deadline_s:
                self.add(t); alpha=1
            while len(e.uavs)>1 and need/((len(e.uavs)-1)*c.paper.cpu_hz)<c.assumptions.deadline_s and self.beta==0:
                u=min((u for u in e.uavs if not u.fixed),key=lambda u:u.battery)
                # Queue transfers are retained and explicitly retransmitted on exit.
                queue=e.retire(u,t)
                for task in queue: task.tx_remaining_s=-1
                tasks=queue+tasks; alpha=1
            if self.policy=='proposed' and self.success<1 and alpha==0:
                self.add(t); alpha=1; self.beta=1
        if target is not None:
            while len(e.uavs)<target: self.add(t); alpha=1
            while len(e.uavs)>target:
                u=min((u for u in e.uavs if not u.fixed),key=lambda u:u.battery)
                queue=e.retire(u,t)
                for task in queue: task.tx_remaining_s=-1
                tasks=queue+tasks; alpha=1
        if alpha: e.redeploy(positions,t)
        allocate(e.uavs,tasks,c)
        records,loads=e.service(t)
        self.success=np.mean([r['success'] for r in records]) if records else 1.
        self.previous_count=count
        return dict(slot=slot,time_h=t/3600,users=count,predicted_users=predicted_count,
                    required_cycles=sum(x.cycles for x in tasks),predicted_cycles=need,
                    active_uavs=len(e.uavs),success_rate=self.success,load_sd=float(np.std([x['tasks'] for x in loads])),
                    completed=sum(r['success'] for r in records),failed=sum(1-r['success'] for r in records)),records,loads
