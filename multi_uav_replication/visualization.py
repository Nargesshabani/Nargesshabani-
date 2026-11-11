from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read(path):
    with open(path) as f:return list(csv.DictReader(f))
def numbers(rows,key):return np.array([float(r[key]) for r in rows])
def figures(root):
    root=Path(root);out=root/'figures';out.mkdir(exist_ok=True)
    result=root/'results'
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140,'savefig.dpi':300,'pdf.fonttype':42})
    def save(fig,name):
        fig.text(.5,.005,'Conditional replication • synthetic demand • see reproducibility report',ha='center',fontsize=7)
        fig.tight_layout(rect=(0,.03,1,1))
        fig.savefig(out/(name+'.png'));fig.savefig(out/(name+'.pdf'));plt.close(fig)
    users=read(result/'clustering_users.csv');centers=read(result/'clustering_centers.csv')
    fig,axes=plt.subplots(1,3,figsize=(11,3.6))
    for n,ax in zip((2,3,4),axes):
        rr=[r for r in users if int(r['n'])==n];cc=[r for r in centers if int(r['n'])==n]
        ax.scatter(numbers(rr,'x'),numbers(rr,'y'),c=numbers(rr,'cluster'),s=14,cmap='tab10')
        ax.scatter(numbers(cc,'x'),numbers(cc,'y'),marker='*',s=120,c='black');ax.set(xlim=(0,500),ylim=(0,500),xlabel='x (m)',ylabel='y (m)',title=f'{n} UAVs; fixed center retained')
    save(fig,'fig02_clustering')
    rr=read(result/'prediction.csv');fig,ax=plt.subplots(figsize=(7,3.5))
    ax.scatter(numbers(rr,'time_h'),numbers(rr,'actual_users'),s=8,label='Synthetic actual')
    ax.plot(numbers(rr,'time_h'),numbers(rr,'predicted_users'),c='tab:red',label='BP next-slot prediction')
    ax.set(xlabel='Time (h)',ylabel='Ground devices');ax.legend();save(fig,'fig03_prediction')
    rr=read(result/'training_loss.csv');fig,ax=plt.subplots(figsize=(7,3.5))
    for method in ('sgd','rmsprop','adam'):
        rows=[r for r in rr if r['optimizer']==method];ax.plot(numbers(rows,'epoch'),numbers(rows,'mse'),label=method)
    ax.set(xlabel='Epoch',ylabel='Training MSE (devices²)');ax.legend();save(fig,'fig04_bp_convergence')
    rr=read(result/'daily_metrics.csv')
    for field,name,ylabel in [('active_uavs','fig05_active_uavs','Active UAVs'),('success_rate','fig06_failure','Deadline failure fraction')]:
        fig,ax=plt.subplots(figsize=(8,3.8))
        for policy in ('fixed','prediction','proposed','enumeration'):
            rows=[r for r in rr if r['policy']==policy]
            y=numbers(rows,field);y=1-y if field=='success_rate' else y
            ax.plot(numbers(rows,'time_h'),y,label=policy,linewidth=1)
        ax.set(xlabel='Time (h)',ylabel=ylabel);ax.legend(ncol=2);save(fig,name)
    rr=read(result/'short_comparison.csv');fig,ax=plt.subplots(figsize=(7,3.5))
    for method in ('proposed','greedy','count_optimum'):
        rows=[r for r in rr if r['method']==method and r['uav_id']=='0']
        ax.plot(numbers(rows,'slot'),numbers(rows,'queue_sd'),label=method)
    ax.set(xlabel='Slot',ylabel='Task-count standard deviation');ax.legend();save(fig,'fig07_load_sd')
    for field,name,label in [('tasks','fig08_task_load','Assigned tasks'),('battery_j','fig09_battery','Battery (kJ); flight excluded')]:
        fig,axes=plt.subplots(1,2,figsize=(10,3.8),sharey=True)
        for method,ax in zip(('proposed','greedy'),axes):
            for j in range(5):
                rows=[r for r in rr if r['method']==method and int(r['uav_id'])==j]
                y=numbers(rows,field)/(1000 if field=='battery_j' else 1)
                ax.plot(numbers(rows,'slot'),y,label=f'UAV {j}')
            ax.set(xlabel='Slot',ylabel=label,title=method);ax.legend(fontsize=7,ncol=2)
        save(fig,name)
    rr=read(result/'energy_ledger.csv');components=sorted(set(r['component'] for r in rr));policies=('fixed','prediction','proposed','enumeration')
    fig,ax=plt.subplots(figsize=(8,4));bottom=np.zeros(4)
    for component in components:
        val=np.array([sum(float(r['joules']) for r in rr if r['policy']==p and r['component']==component)/1e6 for p in policies])
        ax.bar(policies,val,bottom=bottom,label=component);bottom+=val
    ax.set(ylabel='Accounted energy (MJ)');ax.legend(fontsize=7,ncol=2);save(fig,'total_energy')
    rr=read(result/'uav_events.csv');fig,axes=plt.subplots(2,2,figsize=(10,6),sharex=True)
    for policy,ax in zip(policies,axes.ravel()):
        for kind in ('launch','exit','replacement'):
            times=sorted(float(r['time_s'])/3600 for r in rr if r['policy']==policy and r['kind']==kind)
            ax.step([0]+times,[0]+list(range(1,len(times)+1)),where='post',label=kind)
        ax.set(xlabel='Time (h)',ylabel='Cumulative events',title=policy);ax.legend(fontsize=8)
    save(fig,'entry_exit_events')
