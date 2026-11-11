"""Equations 1–7. Link arrays broadcast; rates are bits/s."""
import numpy as np

def distance(users, uavs):
    return np.linalg.norm(np.asarray(users)[:,None,:]-np.asarray(uavs)[None,:,:],axis=-1)

def los_probability(d, height, cfg):
    p,a=cfg.paper,cfg.assumptions
    angle=np.arctan(np.asarray(height)/np.asarray(d))
    if a.angle_unit=='degrees': angle=np.degrees(angle)
    elif a.angle_unit!='radians': raise ValueError('angle_unit')
    return 1/(1+p.los_a*np.exp(-p.los_b*(angle-p.los_a)))

def path_losses(d,cfg):
    a=cfg.assumptions
    fs=20*np.log10(4*np.pi*a.carrier_hz*np.asarray(d)/299792458.)
    return fs+a.excess_los_db,fs+a.excess_nlos_db

def average_loss(d,height,cfg):
    prob=los_probability(d,height,cfg); lo,nlo=path_losses(d,cfg)
    return prob*lo+(1-prob)*nlo

def rate(d,height,cfg):
    p=cfg.paper
    transmit_w=10**((p.transmit_dbm-30)/10)
    return p.bandwidth_hz*np.log2(1+transmit_w*10**(-average_loss(d,height,cfg)/10)/cfg.assumptions.noise_w)

def transmission_time(bits,d,height,cfg):
    mode=cfg.assumptions.transmission_numerator
    if mode not in ('task_bits','printed_distance'): raise ValueError('transmission_numerator')
    numerator=bits if mode=='task_bits' else d
    return np.asarray(numerator)/rate(d,height,cfg)

def communication_energy(seconds,cfg):
    return np.asarray(seconds)*cfg.paper.communication_w
