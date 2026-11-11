"""Shared task-service engine for all policies; serial radio then CPU per UAV."""
import numpy as np
from communication_model import transmission_time
from computation_model import computation_energy
from energy_model import hover_power,route,alert
from uav import UAV

class Environment:
    def __init__(self,cfg):
        self.cfg=cfg; self.uavs=[]; self.events=[]; self.energy=[]; self.next_id=0; self.ready={}; self.motion_until={}
        self.launch(np.array(cfg.assumptions.base_xy),0,True)
    def event(self,time,kind,u,**kwargs):
        self.events.append(dict(time_s=float(time),kind=kind,uav_id=u.id,**kwargs))
    def launch(self,xy,time,fixed=False):
        c=self.cfg; e,dt=route(xy,c)
        u=UAV(self.next_id,np.array(xy,float),c.paper.battery_j-e,fixed); self.next_id+=1
        self.uavs.append(u); self.ready[u.id]=time+dt; self.motion_until[u.id]=time+dt
        self.event(time,'launch',u,arrival_s=time+dt,fixed=fixed)
        self.energy.append(dict(time_s=time,uav_id=u.id,component='launch_flight',joules=e))
        return u
    def charge(self,u,e,time,component):
        u.battery-=e
        self.energy.append(dict(time_s=float(time),uav_id=u.id,component=component,joules=float(e)))
        if u.battery < -1e-6: raise RuntimeError('battery exhausted: invalid energy configuration')
    def retire(self,u,time):
        e,dt=route(u.xy,self.cfg,True)
        if u.battery+1e-7<e: raise RuntimeError('C5 landing reserve violation')
        self.charge(u,e,time,'return_flight'); self.event(time,'exit',u,arrival_s=time+dt,battery_after_j=u.battery)
        self.uavs.remove(u)
        return u.queue
    def replace(self,u,time):
        c=self.cfg; new=self.launch(u.xy,time,u.fixed)
        _,dt=route(u.xy,c)
        # Old UAV supplies rendezvous coverage; new aircraft then assumes role.
        # Task service during this interval is approximated by the task-slot engine.
        self.charge(u,hover_power(c)*dt,time,'replacement_hover')
        queue=self.retire(u,time+dt); new.queue=queue
        self.ready[new.id]=time  # old aircraft covers until new arrives
        for task in queue: task.assigned_id=new.id
        self.event(time,'replacement',new,old_id=u.id,rendezvous_s=time+dt)
        return new
    def replace_low(self,time):
        for u in list(self.uavs):
            if u.battery<=alert(u.xy,u.comm_w,u.compute_w,self.cfg): self.replace(u,time)
    def redeploy(self,users,time):
        from ls_fcm import fit
        from energy_model import flight
        moving=[u for u in self.uavs if not u.fixed]
        if not moving or not len(users): return
        centers,_,_=fit(users,np.array([u.xy for u in moving]),self.cfg)
        for u,xy in zip(moving,centers):
            e,dt=flight(np.linalg.norm(xy-u.xy),'horizontal',self.cfg)
            landing,_=route(xy,self.cfg,True)
            if u.battery<e+landing: u=self.replace(u,time)
            self.charge(u,e,time,'redeployment_flight'); u.xy=np.array(xy)
            self.motion_until[u.id]=max(time,self.motion_until.get(u.id,time))+dt
            if self.ready.get(u.id,time)>time: self.ready[u.id]=self.motion_until[u.id]
            # Existing servers continue service in flight; target geometry used.
            self.event(time,'redeploy',u,x_m=xy[0],y_m=xy[1],travel_s=dt)
    def service(self,time):
        c=self.cfg; records=[]; loads=[]; p=hover_power(c)
        for u in list(self.uavs):
            loads.append(dict(time_s=time,uav_id=u.id,tasks=len(u.queue),battery_j=u.battery))
            cursor=max(time,self.ready.get(u.id,time)); tx_total=0.; cpu_energy=0.
            new_queue=[]
            for task in u.queue:
                d=np.hypot(np.linalg.norm(task.xy-u.xy),c.assumptions.height_m)
                if task.tx_remaining_s<0: task.tx_remaining_s=float(transmission_time(task.bits,d,c.assumptions.height_m,c))
                expiry=task.arrival_s+task.deadline_s
                available=max(0,min(time+c.paper.slot_s,expiry)-cursor)
                tx=min(available,task.tx_remaining_s); task.tx_remaining_s-=tx; cursor+=tx
                tx_total+=tx; available-=tx
                cycles=min(task.cycles_remaining,available*c.paper.cpu_hz)
                ce=float(computation_energy(cycles,task.bits,d,c)); cpu_energy+=ce
                task.cycles_remaining-=cycles; cursor+=cycles/c.paper.cpu_hz
                done=task.cycles_remaining<=1e-5 and task.tx_remaining_s<=1e-10
                if done or expiry<=time+c.paper.slot_s:
                    records.append(dict(task_id=task.id,slot=task.slot,uav_id=u.id,arrival_s=task.arrival_s,
                        finish_s=cursor if done else expiry,success=int(done),delay_s=cursor-task.arrival_s if done else task.deadline_s,
                        bits=task.bits,cycles=task.cycles,remaining_cycles=task.cycles_remaining))
                else: new_queue.append(task)
            u.queue=new_queue
            self.charge(u,tx_total*c.paper.communication_w,time,'communication')
            self.charge(u,cpu_energy,time,'computation')
            u.comm_w=tx_total*c.paper.communication_w/c.paper.slot_s
            u.compute_w=cpu_energy/c.paper.slot_s
            # Continuous hover reserve checks between 5-min demand updates.
            clock=min(time+c.paper.slot_s,max(time,self.motion_until.get(u.id,time)))
            remaining=time+c.paper.slot_s-clock
            while remaining>1e-9:
                threshold=alert(u.xy,u.comm_w,u.compute_w,c)
                until=max(0.,(u.battery-threshold)/p)
                span=min(remaining,until)
                self.charge(u,p*span,clock,'hover'); remaining-=span; clock+=span
                if remaining>1e-9:
                    u=self.replace(u,clock)
                    # Rendezvous hover was charged to outgoing aircraft in replace().
                    covered=min(remaining,max(0,self.motion_until[u.id]-clock))
                    remaining-=covered; clock+=covered
                    if u.battery<=threshold: raise RuntimeError('full battery cannot meet EAlert')
        return records,loads
