from dataclasses import dataclass, field

import numpy as np


@dataclass
class StandardTrack:
    # dataclass for standardized track after data is read in and wrangled
    group: str  # can change to enum
    x: np.ndarray = field(repr=False)  # x coordinate
    y: np.ndarray = field(repr=False)  # y coordinate
    t: np.ndarray = field(repr=False)  # time
    r: np.ndarray = field(repr=False)  # radius
    theta: np.ndarray = field(repr=False)  # angular position
    activity: np.ndarray = field(repr=False)  # step distance
    turn: np.ndarray = field(repr=False)  # turn angle
    p_plus_plus: np.ndarray = field(repr=False)  # p++
    p_plus_minus: np.ndarray = field(repr=False)  # p+-
    p_plus_zero: np.ndarray = field(repr=False)  # p+0
    p_zero_plus: np.ndarray = field(repr=False)  # p0+
    p_zero_zero: np.ndarray = field(repr=False)  # p00
    coverage_bins: np.ndarray = field(repr=False)  # bin visited
    n_bins: float  # number of bins
    coverage: np.ndarray = field(repr=False)  # coverage
    percent_coverage: np.ndarray = field(repr=False)  # percent coverage
    pica: np.ndarray = field(repr=False)  # percent of individual coverage asymptote
    pica_asymptote: float  # individual coverage asymptote
    pgca: np.ndarray = field(repr=False)  # percent of group coverage asymptote
    pgca_asymptote: float  # individual coverage asymptote

    def set_pgca(self, input_pgca, input_pgca_a):
        self.pgca = input_pgca
        self.pgca_asymptote = input_pgca_a
