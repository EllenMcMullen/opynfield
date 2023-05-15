from dataclasses import dataclass


@dataclass
class Defaults:
    # what angle should we use to create the bins for coverage (degrees)
    node_size: float = 0.1

