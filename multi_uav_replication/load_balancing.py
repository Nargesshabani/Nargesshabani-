"""Algorithm 3: cluster preallocation, retention, nearest-pool choice, FIFO."""
import numpy as np
from ls_fcm import hard_assignment

def allocate(uavs,tasks,cfg):
    if not uavs: raise ValueError('no UAV')
    if tasks:
        clusters=hard_assignment(np.array([x.xy for x in tasks]),np.array([u.xy for u in uavs]),cfg)
        for task,j in zip(tasks,clusters):
            task.assigned_id=uavs[j].id; uavs[j].queue.append(task)
    average=sum(len(u.queue) for u in uavs)//len(uavs)
    pool=[]
    for u in uavs:
        # Earlier-slot tasks retained preferentially, per text accompanying pseudocode.
        u.queue.sort(key=lambda task:(task.slot,task.id))
        if len(u.queue)>average:
            pool.extend(u.queue[average:]); u.queue=u.queue[:average]
    for u in uavs:
        while len(u.queue)<=average and pool:  # printed <=, not silently changed
            j=min(range(len(pool)),key=lambda j:(np.linalg.norm(pool[j].xy-u.xy),pool[j].id))
            task=pool.pop(j)
            if task.assigned_id!=u.id:
                task.tx_remaining_s=-1.  # retransmission on handoff, explicit assumption
            task.assigned_id=u.id; u.queue.append(task)
    if pool: raise RuntimeError('unassigned task pool')
    for u in uavs: u.queue.sort(key=lambda task:(task.slot,task.id))
