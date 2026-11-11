"""Paper baselines with explicit enumeration scope."""
import itertools
import numpy as np
from communication_model import transmission_time
from objectives import p1_feasible,load_variance

def minimum_count(cycles,cfg):
    for n in range(1,cfg.assumptions.max_uavs+1):
        if p1_feasible(cycles,n,cfg): return n
    raise RuntimeError('count enumeration exceeded max_uavs')

def greedy(uavs,tasks,cfg):
    """Nearest available UAV; full-area coverage assumed (no source radius)."""
    budget=[]
    for u in uavs:
        budget.append(sum(float(transmission_time(t.bits,np.hypot(np.linalg.norm(t.xy-u.xy),cfg.assumptions.height_m),cfg.assumptions.height_m,cfg))+t.cycles_remaining/cfg.paper.cpu_hz for t in u.queue))
    for task in tasks:
        order=sorted(range(len(uavs)),key=lambda j:np.linalg.norm(task.xy-uavs[j].xy))
        chosen=order[0]
        for j in order:
            d=np.hypot(np.linalg.norm(task.xy-uavs[j].xy),cfg.assumptions.height_m)
            service=float(transmission_time(task.bits,d,cfg.assumptions.height_m,cfg))+task.cycles/cfg.paper.cpu_hz
            if budget[j]+service<=task.deadline_s:
                chosen=j; break
        u=uavs[chosen]; d=np.hypot(np.linalg.norm(task.xy-u.xy),cfg.assumptions.height_m)
        budget[chosen]+=float(transmission_time(task.bits,d,cfg.assumptions.height_m,cfg))+task.cycles/cfg.paper.cpu_hz
        task.assigned_id=u.id; u.queue.append(task)
    for u in uavs: u.queue.sort(key=lambda t:(t.slot,t.id))

def balanced_counts(m,n):
    q,r=divmod(m,n); return [q+int(j<r) for j in range(n)]

def exhaustive_assignment(m,n,cfg):
    if n**m>cfg.assumptions.enumeration_max_states:
        raise ValueError('literal exhaustive enumeration too large; use exact balanced_counts oracle')
    best=None; value=float('inf')
    for assignment in itertools.product(range(n),repeat=m):
        v=load_variance(np.bincount(assignment,minlength=n))
        if v<value: best,value=assignment,v
    return best,value
