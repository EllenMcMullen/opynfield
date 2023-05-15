import numpy as np
from dataclasses import dataclass
from typing import Callable


def exponential(x, a, b, c):
    y = a * np.exp(b*x) + c
    return y


def fixed_exponential(x, a, b):
    y = a*(np.exp(b*x)-1)
    return y


def linear(x, a, b):
    y = a*x + b
    return y


@dataclass
class CoverageAsymptote:
    f_name: Callable = fixed_exponential
    asymptote_param: int = 0
    asymptote_sign: int = np.sign(-1)
    initial_parameters: tuple[float, float] = (-0.01, -0.01)
    parameter_bounds: tuple[list[int], list[int]] = ([-10, -10], [0, 0])
    max_f_eval: int = 4000

