"""Three-layer backpropagation MLP. All undisclosed choices in config."""
import numpy as np
from task_generator import demand

def training_data(cfg):
    a,p=cfg.assumptions,cfg.paper; rows=[]; labels=[]; days=[]
    for day in range(a.training_days):
        counts=demand(day,cfg)
        for t in range(p.slots-1):
            rows.append([day,t,counts[t]]); labels.append(counts[t+1]); days.append(day)
    return np.asarray(rows,float),np.asarray(labels,float)[:,None],np.asarray(days)

class BP:
    def __init__(self,cfg,optimizer='adam'):
        self.cfg=cfg; self.optimizer=optimizer
    def fit(self,x,y):
        a=self.cfg.assumptions; rng=np.random.default_rng(a.seed)
        self.xmean=x.mean(0); self.xstd=np.maximum(x.std(0),1)
        self.ymean=y.mean(0); self.ystd=np.maximum(y.std(0),1)
        x=(x-self.xmean)/self.xstd; y=(y-self.ymean)/self.ystd
        self.params=[rng.normal(0,1/np.sqrt(3),(3,a.bp_hidden)),np.zeros((1,a.bp_hidden)),
                     rng.normal(0,1/np.sqrt(a.bp_hidden),(a.bp_hidden,1)),np.zeros((1,1))]
        moments=[np.zeros_like(z) for z in self.params]; variance=[z.copy() for z in moments]
        self.loss=[]; step=0
        for _ in range(a.bp_epochs):
            order=rng.permutation(len(x))
            for start in range(0,len(x),a.bp_batch):
                ix=order[start:start+a.bp_batch]; xx=x[ix]; yy=y[ix]
                w,b,v,c=self.params; h=np.tanh(xx@w+b); out=h@v+c
                grad=2*(out-yy)/len(ix); gh=(grad@v.T)*(1-h*h)
                grads=[xx.T@gh,gh.sum(0,keepdims=True),h.T@grad,grad.sum(0,keepdims=True)]
                step+=1
                for j,g in enumerate(grads):
                    if self.optimizer=='adam':
                        moments[j]=a.adam_beta1*moments[j]+(1-a.adam_beta1)*g; variance[j]=a.adam_beta2*variance[j]+(1-a.adam_beta2)*g*g
                        update=(moments[j]/(1-a.adam_beta1**step))/(np.sqrt(variance[j]/(1-a.adam_beta2**step))+a.optimizer_epsilon)
                    elif self.optimizer=='rmsprop':
                        variance[j]=a.rmsprop_decay*variance[j]+(1-a.rmsprop_decay)*g*g; update=g/(np.sqrt(variance[j])+a.optimizer_epsilon)
                    elif self.optimizer=='sgd': update=g
                    else: raise ValueError(self.optimizer)
                    self.params[j]-=a.bp_learning_rate*update
            w,b,v,c=self.params
            self.loss.append(float(np.mean(((np.tanh(x@w+b)@v+c-y)*self.ystd)**2)))
        return self
    def predict(self,x):
        w,b,v,c=self.params; xx=(np.asarray(x)-self.xmean)/self.xstd
        return np.maximum(0,(np.tanh(xx@w+b)@v+c)*self.ystd+self.ymean).ravel()
    def save(self,path):
        np.savez(path,**{f'p{j}':z for j,z in enumerate(self.params)},xmean=self.xmean,xstd=self.xstd,ymean=self.ymean,ystd=self.ystd)
    @classmethod
    def load(cls,path,cfg):
        z=np.load(path); model=cls(cfg); model.params=[z[f'p{j}'] for j in range(4)]
        for name in ('xmean','xstd','ymean','ystd'): setattr(model,name,z[name])
        return model
