"""Reproducible experiment suite; every output originates in executed code."""
from pathlib import Path
from copy import deepcopy
import csv,json,platform,sys
import numpy as np
from bp_prediction import BP,training_data
from task_generator import demand,tasks_for_slot
from mneea import MNEEA
from uav import UAV
from ls_fcm import fit,hard_assignment
from load_balancing import allocate
from baseline_methods import greedy,balanced_counts,exhaustive_assignment
from communication_model import transmission_time
from computation_model import computation_energy
from energy_model import constants,hover_power,flight

def write_csv(path,rows):
    rows=list(rows)
    if not rows: Path(path).write_text(''); return
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with open(path,'w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(rows)

def clustering(cfg,out):
    rng=np.random.default_rng(cfg.assumptions.seed); users=rng.uniform(0,500,(70,2)); centers_rows=[]; user_rows=[]; convergence=[]
    for n in (2,3,4):
        angles=np.arange(n-1)*2*np.pi/(n-1)
        initial=250+80*np.column_stack((np.cos(angles),np.sin(angles)))
        centers,u,trace=fit(users,initial,cfg); all_centers=np.vstack(([250,250],centers))
        labels=hard_assignment(users,all_centers,cfg)
        for j,xy in enumerate(all_centers): centers_rows.append(dict(n=n,uav=j,x=xy[0],y=xy[1]))
        for j,(xy,label) in enumerate(zip(users,labels)): user_rows.append(dict(n=n,user=j,x=xy[0],y=xy[1],cluster=label))
        for j,g in enumerate(trace): convergence.append(dict(n=n,iteration=j+1,objective=g))
    write_csv(out/'clustering_centers.csv',centers_rows);write_csv(out/'clustering_users.csv',user_rows)
    write_csv(out/'clustering_convergence.csv',convergence)

def prediction(cfg,out):
    x,y,days=training_data(cfg)
    models={}; losses=[]; scores=[]
    holdout=int(cfg.assumptions.training_days*cfg.assumptions.training_fraction); train=days<holdout
    for optimizer in ('sgd','rmsprop','adam'):
        model=BP(cfg,optimizer).fit(x[train],y[train]); models[optimizer]=model
        pred=model.predict(x[~train]); error=pred-y[~train,0]
        scores.append(dict(optimizer=optimizer,holdout_mse=float(np.mean(error**2)),holdout_mae=float(np.mean(abs(error))),train_days=holdout,heldout_days=cfg.assumptions.training_days-holdout))
        losses.extend(dict(optimizer=optimizer,epoch=j+1,mse=v) for j,v in enumerate(model.loss))
    day=cfg.assumptions.training_days; actual=demand(day,cfg)
    # At slot t use date,time,count from slot t-1; first point has no history.
    predicted=np.r_[actual[0],models['adam'].predict(np.column_stack((np.full(len(actual)-1,day),np.arange(len(actual)-1),actual[:-1])))]
    rows=[dict(slot=t,time_h=t*cfg.paper.slot_s/3600,actual_users=int(v),predicted_users=float(p)) for t,(v,p) in enumerate(zip(actual,predicted))]
    write_csv(out/'prediction.csv',rows);write_csv(out/'training_loss.csv',losses);write_csv(out/'prediction_scores.csv',scores)
    write_csv(out/'training_dataset.csv',(dict(day=int(d),slot=int(xx[1]),current_users=int(xx[2]),next_users=int(yy[0]),split='train' if d<holdout else 'holdout') for xx,yy,d in zip(x,y,days)))
    models['adam'].save(out/'bp_model.npz')
    return actual,predicted

def daily(cfg,out,actual,predicted):
    metrics=[]; results=[]; loads=[]; events=[]; energy=[]
    for policy in ('fixed','prediction','proposed','enumeration'):
        model=MNEEA(cfg,policy); rng=np.random.default_rng(cfg.assumptions.seed+77); next_id=0
        for slot,(count,pred) in enumerate(zip(actual,predicted)):
            positions=rng.uniform(0,cfg.paper.area_m,(int(count),2))
            tasks=tasks_for_slot(int(count),slot,rng,cfg,next_id,positions); next_id+=len(tasks)
            row,rr,ll=model.step(slot,int(count),float(pred),tasks,positions)
            metrics.append(dict(policy=policy,**row))
            results.extend(dict(policy=policy,**r) for r in rr);loads.extend(dict(policy=policy,**r) for r in ll)
        events.extend(dict(policy=policy,**e) for e in model.env.events)
        energy.extend(dict(policy=policy,**e) for e in model.env.energy)
    write_csv(out/'daily_metrics.csv',metrics);write_csv(out/'task_results.csv',results)
    write_csv(out/'daily_loads.csv',loads);write_csv(out/'uav_events.csv',events);write_csv(out/'energy_ledger.csv',energy)
    summary=[]
    for policy in ('fixed','prediction','proposed','enumeration'):
        mm=[r for r in metrics if r['policy']==policy]; rr=[r for r in results if r['policy']==policy]
        ee=[r for r in energy if r['policy']==policy]
        summary.append(dict(policy=policy,tasks=len(rr),success_rate=sum(r['success'] for r in rr)/max(1,len(rr)),mean_active=float(np.mean([r['active_uavs'] for r in mm])),mean_load_sd=float(np.mean([r['load_sd'] for r in mm])),energy_j=sum(r['joules'] for r in ee),replacements=sum(e['kind']=='replacement' and e['policy']==policy for e in events),landings_safe=all(e.get('battery_after_j',0)>=-1e-7 for e in events if e['policy']==policy)))
    write_csv(out/'summary.csv',summary)
    return summary

def short_comparison(cfg,out):
    """Figs.7–9 analogue: shared 70-device positions, five stationary UAVs."""
    a,p=cfg.assumptions,cfg.paper; rng=np.random.default_rng(a.seed+88)
    positions=rng.uniform(0,p.area_m,(a.short_users,2))
    n=a.short_uavs; theta=np.arange(n-1)*2*np.pi/(n-1)
    centers,_,_=fit(positions,250+80*np.column_stack((np.cos(theta),np.sin(theta))),cfg)
    centers=np.vstack(([250,250],centers)); data=[]; oracle=[]
    batteries={name:np.full(n,p.battery_j) for name in ('proposed','greedy','count_optimum')}
    for slot in range(a.short_slots):
        tasks=tasks_for_slot(a.short_users,slot,rng,cfg,slot*a.short_users,positions)
        oracle.append(dict(slot=slot,tasks=len(tasks),sd=float(np.std(balanced_counts(len(tasks),n)))))
        for name in batteries:
            uavs=[UAV(j,xy.copy(),batteries[name][j],j==0) for j,xy in enumerate(centers)]
            copied=deepcopy(tasks)
            if name=='proposed': allocate(uavs,copied,cfg)
            elif name=='greedy': greedy(uavs,copied,cfg)
            else:
                cursor=0
                for u,k in zip(uavs,balanced_counts(len(tasks),n)):
                    u.queue=copied[cursor:cursor+k];cursor+=k
            for u in uavs:
                time=0.; ce=0.; tx=0.; done=0
                for task in u.queue:
                    d=np.hypot(np.linalg.norm(task.xy-u.xy),a.height_m)
                    comm=float(transmission_time(task.bits,d,a.height_m,cfg))
                    time+=comm+task.cycles/p.cpu_hz; tx+=comm*p.communication_w
                    ce+=float(computation_energy(task.cycles,task.bits,d,cfg));done+=int(time<=a.deadline_s)
                # Isolated figure analogue: all allocated tasks run to completion,
                # even if late; report deadline success separately. Flight excluded.
                batteries[name][u.id]-=ce+tx
                data.append(dict(method=name,slot=slot,uav_id=u.id,tasks=len(u.queue),success=done,communication_j=tx,computation_j=ce,battery_j=batteries[name][u.id],queue_sd=float(np.std([len(v.queue) for v in uavs]))))
    write_csv(out/'short_comparison.csv',data);write_csv(out/'count_optimum.csv',oracle)
    checks=[]
    for m in range(0,9):
        assignment,value=exhaustive_assignment(m,3,cfg)
        checks.append(dict(tasks=m,uavs=3,exhaustive_variance=value,analytic_variance=float(np.var(balanced_counts(m,3)))))
    write_csv(out/'enumeration_verification.csv',checks)

def sensitivity(cfg,out):
    rows=[]
    for angle in ('radians','degrees'):
        for mode in ('total_cycles','literal_distance','data_multiplied'):
            cc=deepcopy(cfg);cc.assumptions.angle_unit=angle;cc.assumptions.compute_energy_mode=mode
            for d in (50.,250.,500.):
                rows.append(dict(angle=angle,compute_mode=mode,distance_m=d,tx_s=float(transmission_time(6e6,d,cc.assumptions.height_m,cc)),compute_j=float(computation_energy(1e8,6e6,d,cc))))
    write_csv(out/'model_sensitivity.csv',rows)
    rows=[]
    for mode in ('horizontal','up','down'):
        for length in (0,30,100,500):
            e,t=flight(length,mode,cfg)
            rows.append(dict(mode=mode,distance_m=length,time_s=t,energy_j=e,physical_validity='conditional_source_equation'))
    write_csv(out/'flight_checks.csv',rows)
    rows=[]
    for mode in ('printed','force_balance'):
        cc=deepcopy(cfg);cc.assumptions.horizontal_mode=mode
        for length in (30.,100.,250.,500.):
            energy,seconds=flight(length,'horizontal',cc)
            rows.append(dict(horizontal_mode=mode,distance_m=length,energy_j=energy,time_s=seconds,battery_fraction=energy/cc.paper.battery_j))
    write_csv(out/'horizontal_mode_sensitivity.csv',rows)
    # Single shared static snapshot isolates unspecified latency and angle settings.
    rows=[];a=cfg.assumptions
    rng=np.random.default_rng(a.seed+999);positions=rng.uniform(0,cfg.paper.area_m,(a.short_users,2))
    snapshot=tasks_for_slot(a.short_users,0,rng,cfg,positions=positions)
    n=a.short_uavs;theta=np.arange(n-1)*2*np.pi/(n-1)
    movable,_,_=fit(positions,250+80*np.column_stack((np.cos(theta),np.sin(theta))),cfg)
    centers=np.vstack(([250,250],movable))
    for angle in ('radians','degrees'):
        for deadline in a.deadline_sweep:
            cc=deepcopy(cfg);cc.assumptions.angle_unit=angle;cc.assumptions.deadline_s=deadline
            uavs=[UAV(j,xy,cfg.paper.battery_j) for j,xy in enumerate(centers)]
            allocate(uavs,deepcopy(snapshot),cc);success=0
            for u in uavs:
                elapsed=0.
                for task in u.queue:
                    d=np.hypot(np.linalg.norm(task.xy-u.xy),a.height_m)
                    elapsed+=float(transmission_time(task.bits,d,a.height_m,cc))+task.cycles/cfg.paper.cpu_hz
                    success+=int(elapsed<=deadline)
            rows.append(dict(angle=angle,deadline_s=deadline,tasks=len(snapshot),success_rate=success/max(1,len(snapshot))))
    write_csv(out/'deadline_angle_sensitivity.csv',rows)
    from objectives import printed_p2,load_variance
    write_csv(out/'p2_notation_audit.csv',[dict(lengths=str(loads),printed_p2=printed_p2(loads),interpreted_variance=load_variance(loads)) for loads in ([10,0,0],[4,3,3],[1,1,1])])

def run(cfg,root):
    root=Path(root);out=root/'results';out.mkdir(parents=True,exist_ok=True)
    cfg.save(out/'config.json');clustering(cfg,out)
    actual,predicted=prediction(cfg,out); summary=daily(cfg,out,actual,predicted)
    short_comparison(cfg,out);sensitivity(cfg,out)
    (out/'provenance.json').write_text(json.dumps(dict(python=sys.version,numpy=np.__version__,platform=platform.platform(),seed=cfg.assumptions.seed,source='conditional implementation using synthetic demand; not exact published result reproduction'),indent=2))
    return summary
