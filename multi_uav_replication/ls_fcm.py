"""Algorithm 1, Eqs.16–18; not replaced by conventional FCM."""
import numpy as np

def tau(users,centers,height):
    return np.sum((np.asarray(users)[:,None,:2]-np.asarray(centers)[None,:,:2])**2,axis=-1)+height**2

def membership(path_loss,eta):
    if eta<=1: raise ValueError('eta must exceed one')
    path_loss=np.asarray(path_loss,float)
    if path_loss.ndim!=2 or path_loss.shape[1]==0 or np.any(path_loss<0): raise ValueError('invalid tau')
    zeros=path_loss==0; haszero=zeros.any(axis=1)
    logw=-2/(eta-1)*np.log(np.maximum(path_loss,np.finfo(float).tiny))
    logw-=logw.max(axis=1,keepdims=True); w=np.exp(logw)
    w/=w.sum(axis=1,keepdims=True)
    w[haszero]=zeros[haszero]/zeros[haszero].sum(axis=1,keepdims=True)
    return w

def objective(u,path_loss,eta):
    return float(np.sum(u**eta*path_loss))

def fit(users,current_centers,cfg):
    a=cfg.assumptions; centers=np.array(current_centers,float).reshape(-1,2).copy()
    users=np.asarray(users)
    if not len(centers) or not len(users): return centers,np.empty((len(users),len(centers))),[]
    u=membership(tau(users,centers,a.height_m),a.fuzzy_eta)
    previous=1.; trace=[]
    for _ in range(a.fuzzy_iterations):
        w=u**a.fuzzy_eta
        centers=(w.T@users[:,:2])/w.sum(axis=0)[:,None]
        g=objective(u,tau(users,centers,a.height_m),a.fuzzy_eta)
        trace.append(g)
        u=membership(tau(users,centers,a.height_m),a.fuzzy_eta)
        delta=g-previous; previous=g
        if abs(delta)<=a.fuzzy_tolerance: break
    return centers,u,trace

def hard_assignment(users,positions,cfg):
    # Include fixed UAV for assignment; fixed center is never optimized.
    return np.argmax(membership(tau(users,positions,cfg.assumptions.height_m),cfg.assumptions.fuzzy_eta),axis=1)
