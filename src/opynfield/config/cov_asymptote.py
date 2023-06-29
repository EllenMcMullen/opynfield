import numpy as np
from dataclasses import dataclass
from typing import Callable


def exponential(x, a, b, c):
    # exponential decay
    y = a * np.exp(b * x) + c
    # c is asymptote and positive
    return y


def fixed_exponential(x, a, b):
    # growth towards an asymptote
    y = a * (np.exp(b * x) - 1)
    # parameter 'a' is asymptote and negative
    return y


def linear(x, a, b):
    # linear
    y = a * x + b
    # no asymptote -> ignore pica and pgca results
    return y


@dataclass
class CoverageAsymptote:
    f_name: Callable = (
        fixed_exponential  # function to model time coverage relationship with
    )
    asymptote_param: int = (
        0  # which parameter of the function is the asymptote magnitude (index at 0)
    )
    asymptote_sign: int = np.sign(
        -1
    )  # what sign is the asymptote calculated with (based on bounds & initial params)
    initial_parameters: tuple[float, float] = (
        -0.01,
        -0.01,
    )  # parameters to start model with
    parameter_bounds: tuple[list[int], list[int]] = (
        [-10, -10],
        [0, 0],
    )  # bounds on the parameters
    max_f_eval: int = 4000  # increase if you run into runtime errors
