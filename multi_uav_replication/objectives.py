"""Optimization objectives and constraints, Eqs.14–15."""
import numpy as np

def p1_feasible(cycles,active,cfg):
    return cycles<cfg.assumptions.deadline_s*active*cfg.paper.cpu_hz

def load_variance(lengths):
    return float(np.var(lengths)) if len(lengths) else 0.

def constraints(delays,batteries,landing,cfg):
    return {'C4_delay':bool(np.all(np.asarray(delays)<=cfg.assumptions.deadline_s)),
            'C5_landing':bool(np.all(np.asarray(batteries)>=np.asarray(landing)))}


def printed_p2(lengths,active=None):
    """Literal repeated n index in Eq.15; degenerates to zero when N=active."""
    lengths=np.asarray(lengths,float)
    if active is None: active=len(lengths)
    if active<=0: raise ValueError('active count must be positive')
    return float(np.sum((lengths-len(lengths)*lengths/active)**2)/active)
