"""Synthetic demand is an assumption, never the undisclosed original trace."""
import numpy as np
from iot_devices import Task

def demand(day,cfg):
    a,p=cfg.assumptions,cfg.paper
    rng=np.random.default_rng(a.seed+10000+day)
    h=np.arange(p.slots)*p.slot_s/3600
    mean=np.interp(h,a.demand_knots_hours,a.demand_knots_counts)
    mean*=1+rng.normal(0,a.day_amplitude_sd)
    return np.maximum(0,np.rint(mean+rng.normal(0,a.demand_noise_sd,len(h)))).astype(int)

def tasks_for_slot(count,slot,rng,cfg,start_id=0,positions=None):
    a,p=cfg.assumptions,cfg.paper
    if positions is None: positions=rng.uniform(0,p.area_m,(count,2))
    tasks=[]
    for xy in positions:
        if rng.random()<a.arrival_probability:
            tasks.append(Task(start_id+len(tasks),np.array(xy),rng.uniform(*p.data_mb)*8e6,
                              rng.uniform(*p.cycles),slot*p.slot_s,slot,a.deadline_s))
    return tasks
