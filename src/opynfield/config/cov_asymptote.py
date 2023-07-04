import numpy as np
from dataclasses import dataclass
from typing import Callable


def exponential(x, a, b, c):
    """ Fits an exponential model to the data

    :param x: independent data
    :type x: np.ndarray
    :param a: scaling parameter
    :type a: float
    :param b: decay parameter
    :type b: float
    :param c: constant parameter
    :type c: float
    :return: dependent data
    :rtype: np.ndarray
    """
    # exponential decay
    y = a * np.exp(b * x) + c
    # c is asymptote and positive
    return y


def fixed_exponential(x, a, b):
    """Fits a 'fixed exponential' model to the data which anchors the curve at (0, 0)

    :param x: independent data
    :type x: np.ndarray
    :param a: scaling parameter
    :type a: float
    :param b: growth parameter
    :type b: float
    :return: dependent data
    :rtype: np.ndarray
    """
    # growth towards an asymptote
    y = a * (np.exp(b * x) - 1)
    # parameter 'a' is asymptote and negative
    return y


def linear(x, a, b):
    """Fits a linear model to the data

    :param x: independent data
    :type x: np.ndarray
    :param a: slope
    :type a: float
    :param b: intercept
    :type b: float
    :return: dependent data
    :rtype: np.ndarray
    """
    # linear
    y = a * x + b
    # no asymptote -> ignore pica and pgca results
    return y


@dataclass
class CoverageAsymptote:
    """ This dataclass associates relevant information for the model fits needed to calculate a coverage asymptote
    (for PICA and PGCA)

    Attributes:
        f_name (Callable): the function to use in the model fit - be a function that approaches an asymptote as x approaches infinity, defaults to :func:`fixed_exponential`
        asymptote_param (int): which parameter indicates the asymptote magnitude, defaults to 0
        asymptote_sign (int): is the asymptote parameter positive or negative, defaults to -1 (negative)
        initial_parameters (tuple[float]): what p0 to use in curve fitting to find the asymptote, defaults to (-0.1, -0.1)
        parameter_bounds (tuple[list[int]]): what bounds to use in curve fitting to find the asymptote, defaults to ([-10, -10], [0, 0])
        max_f_eval (int): max number of iterations the curve fitting process can take to find the asymptote, defaults to 4000
    """
    f_name: Callable = (
        fixed_exponential  # function to model time coverage relationship with
    )
    asymptote_param: int = (
        0  # which parameter of the function is the asymptote magnitude (index at 0)
    )
    asymptote_sign: int = np.sign(
        -1
    )  # what sign is the asymptote calculated with (based on bounds & initial params)
    initial_parameters: tuple[float] = (
        -0.01,
        -0.01,
    )  # parameters to start model with
    parameter_bounds: tuple[list[int], list[int]] = (
        [-10, -10],
        [0, 0],
    )  # bounds on the parameters
    max_f_eval: int = 4000  # increase if you run into runtime errors
