"""Every unspecified numerical choice is grouped under assumptions."""
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path

@dataclass
class Paper:
    area_m: float = 500.
    slot_s: float = 300.
    slots: int = 288
    data_mb: tuple = (.5, 1.)
    cycles: tuple = (50e6, 150e6)
    cpu_hz: float = 1e9
    communication_w: float = 1.
    battery_j: float = 500e3
    bandwidth_hz: float = 1e6
    transmit_dbm: float = 30.
    acceleration: float = 5.
    max_speed: float = 30.
    weight_n: float = 20.
    density: float = 1.225
    rotor_radius: float = .4
    solidity: float = .05
    drag_profile: float = .012
    omega: float = 300.
    induced_k: float = .1
    los_a: float = 4.88
    los_b: float = .43

@dataclass
class Assumptions:
    seed: int = 2022
    carrier_hz: float = 2e9  # user supplied, unverified in paper
    height_m: float = 30.
    noise_w: float = 1e-13
    excess_los_db: float = 1.
    excess_nlos_db: float = 20.
    angle_unit: str = 'radians'  # literal arctan in Eq.4
    gamma: float = 1e-28
    transmission_numerator: str = 'task_bits'  # printed_distance is dimensionally invalid
    compute_energy_mode: str = 'total_cycles'
    mass_kg: float = 20/9.81
    plate_area: float = .05
    fuselage_drag: float = .6
    horizontal_mode: str = 'force_balance'  # explicit operational repair; printed mode also implemented
    q2_w: float = 0.  # undefined in Eq.12–13; literal conditional evaluation
    deadline_s: float = 1.
    arrival_probability: float = .5
    initial_mobile_radius_m: float = 80.
    base_xy: tuple = (250., 250.)
    fuzzy_eta: float = 2.
    fuzzy_tolerance: float = 1e-5
    fuzzy_iterations: int = 200
    bp_hidden: int = 24
    bp_epochs: int = 800
    bp_learning_rate: float = .01
    bp_batch: int = 128
    training_fraction: float = .8
    adam_beta1: float = .9
    adam_beta2: float = .999
    rmsprop_decay: float = .9
    optimizer_epsilon: float = 1e-8
    deadline_sweep: tuple = (.5, 1., 2., 5., 10.)
    training_days: int = 28
    demand_knots_hours: tuple = (0,1,4,6,7,8,12,16,20,22,24)
    demand_knots_counts: tuple = (20,5,5,75,150,80,110,95,70,35,20)
    demand_noise_sd: float = 7.
    day_amplitude_sd: float = .06
    max_uavs: int = 64  # fail loudly if reached; no unbounded loop
    fixed_uavs: int = 4
    short_users: int = 70
    short_uavs: int = 5
    short_slots: int = 60
    enumeration_max_states: int = 2000000
    expired_tasks: str = 'drop'  # deadline misses logged, removed at deadline

@dataclass
class Config:
    paper: Paper = field(default_factory=Paper)
    assumptions: Assumptions = field(default_factory=Assumptions)
    def save(self, path):
        Path(path).write_text(json.dumps(asdict(self), indent=2)+'\n')
    @classmethod
    def load(cls, path):
        d=json.loads(Path(path).read_text())
        return cls(Paper(**d['paper']), Assumptions(**d['assumptions']))
