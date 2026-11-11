"""Equations 8–9; see docs for Eq.9's conflicting d notation."""
import numpy as np

def computation_time(cycles,cfg):
    return np.asarray(cycles)/cfg.paper.cpu_hz

def computation_energy(cycles,bits,distance,cfg):
    a=cfg.assumptions
    factor={'total_cycles':1.,'literal_distance':distance,'data_multiplied':bits}.get(a.compute_energy_mode)
    if factor is None: raise ValueError('compute_energy_mode')
    return a.gamma*np.asarray(cycles)*factor*cfg.paper.cpu_hz**2
