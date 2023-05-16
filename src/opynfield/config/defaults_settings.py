from dataclasses import dataclass


@dataclass
class Defaults:
    # what angle should we use to create the bins for coverage (degrees)
    node_size: float = 0.1
    # should we save out a csv for each group's component measures?
    save_group_csvs: bool = True

