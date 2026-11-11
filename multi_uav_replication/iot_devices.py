from dataclasses import dataclass
import numpy as np

@dataclass
class Task:
    id: int
    xy: np.ndarray
    bits: float
    cycles: float
    arrival_s: float
    slot: int
    deadline_s: float
    tx_remaining_s: float = -1.
    cycles_remaining: float = -1.
    assigned_id: int = -1
    def __post_init__(self):
        if self.cycles_remaining<0: self.cycles_remaining=self.cycles
