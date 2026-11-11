from dataclasses import dataclass, field
import numpy as np

@dataclass
class UAV:
    id: int
    xy: np.ndarray
    battery: float
    fixed: bool = False
    queue: list = field(default_factory=list)
    comm_w: float = 0.
    compute_w: float = 0.
