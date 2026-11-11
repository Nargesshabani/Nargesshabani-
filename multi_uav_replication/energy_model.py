"""Eq.10–13 verbatim conditional evaluation, including source dimensional issues."""
import numpy as np
from numpy.polynomial.legendre import leggauss

def constants(cfg):
    p=cfg.paper; area=np.pi*p.rotor_radius**2
    q0=p.drag_profile/8*p.density*p.solidity*area*p.omega**3*p.rotor_radius**3
    q1=(1+p.induced_k)*p.weight_n**1.5/(np.sqrt(2)*np.sqrt(2*p.density*area))
    return area,q0,q1

def hover_power(cfg):
    _,q0,q1=constants(cfg); return q0+q1

def horizontal_power(v,acc,cfg):
    p,a=cfg.paper,cfg.assumptions; area,q0,q1=constants(cfg)
    c1=3/(p.omega**2*p.rotor_radius**2); c2=p.density*a.plate_area/(2*p.weight_n)
    c3=a.mass_kg/p.weight_n; c4=p.density*area/p.weight_n
    c5=.5*a.fuselage_drag*p.density*p.solidity*area
    q=c2*v**2+c3*acc*v**2 if a.horizontal_mode=='printed' else c2*v**2+c3*acc
    if a.horizontal_mode not in ('printed','force_balance'): raise ValueError('horizontal_mode')
    inner=np.sqrt(1+q*q+c4*c4*v**4)-c4*v*v
    return q0*(1+c1*v*v)+q1*np.sqrt(1+q*q)*np.sqrt(inner)+c5*v**3

def vertical_power(v,acc,mode,cfg):
    p,a=cfg.paper,cfg.assumptions; area,_,_=constants(cfg)
    z=p.weight_n+(-1 if mode=='up' else 1)*a.mass_kg*acc
    if z<0: raise ValueError('negative thrust in printed vertical equation')
    return a.q2_w+z*v/2+z/2*np.sqrt(v*v+np.sqrt(2*z*p.density*area))

def profile(length,cfg):
    """Return (duration,start_speed,acceleration) segments, including short trips."""
    if length<0: raise ValueError('negative distance')
    if length==0: return []
    p=cfg.paper; peak=min(p.max_speed,np.sqrt(length*p.acceleration))
    ta=peak/p.acceleration; coast=max(0.,(length-peak**2/p.acceleration)/peak)
    return [(ta,0.,p.acceleration),(coast,peak,0.),(ta,peak,-p.acceleration)]

def flight(length,mode,cfg,order=32):
    if mode not in ('horizontal','up','down'): raise ValueError(mode)
    nodes,weights=leggauss(order); energy=0.; duration=0.
    for dt,v0,acc in profile(float(length),cfg):
        ts=(nodes+1)*dt/2; v=v0+acc*ts
        power=horizontal_power(v,acc,cfg) if mode=='horizontal' else vertical_power(v,acc,mode,cfg)
        energy+=float(np.dot(weights,power)*dt/2); duration+=dt
    return energy,duration

def route(xy,cfg,returning=False):
    length=float(np.linalg.norm(np.asarray(xy)-cfg.assumptions.base_xy))
    e,t=flight(length,'horizontal',cfg)
    ev,tv=flight(cfg.assumptions.height_m,'down' if returning else 'up',cfg)
    return e+ev,t+tv

def alert(xy,comm_w,compute_w,cfg):
    landing,_=route(xy,cfg,True); _,tfly=route(xy,cfg)
    return (hover_power(cfg)+comm_w+compute_w)*tfly+landing
