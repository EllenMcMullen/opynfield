from dataclasses import dataclass
from typing import Union
import numpy as np


@dataclass()
class ExponentialModel:
    initial_params: tuple[float, float, float] = (0.1, -0.1, 0.01)
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]] = ((0, -10, 0), (10, 0, 10))
    max_eval: int = 4000
    display_parts: tuple[str] = ('y = ', ' * e ^ (', ' * x) + ')

    @staticmethod
    def model_function(x, a, b, c):
        # Exponential Implementation
        y = a * np.exp(b * x) + c
        return y


@dataclass()
class FixedExponentialModel:
    initial_params: tuple[float, float] = (-0.1, -0.1)
    bounds: tuple[tuple[float, float], tuple[float, float]] = ((-10, -10), (0, 0))
    max_eval: int = 4000
    display_parts: tuple[str] = ('y = ', ' * (e ^ (', ' * x) - 1)')

    @staticmethod
    def model_function(x, a, b):
        # Exponential Implementation
        y = a * (np.exp(b * x) - 1)
        return y


@dataclass()
class LinearIncreaseModel:
    initial_params: tuple[float, float] = (0.1, 0.1)
    bounds: tuple[tuple[float, float], tuple[float, float]] = ((0, 0), (10, 10))
    max_eval: int = 4000
    display_parts: tuple[str] = ('y = ', ' * x + ')

    @staticmethod
    def model_function(x, a, b):
        # Exponential Implementation
        y = (a * x) + b
        return y


@dataclass()
class LinearDecreaseModel:
    initial_params: tuple[float, float] = (-0.1, 0.1)
    bounds: tuple[tuple[float, float], tuple[float, float]] = ((-10, 0), (0, 10))
    max_eval: int = 4000
    display_parts: tuple[str] = ('y = ', ' * x + ')

    @staticmethod
    def model_function(x, a, b):
        # Exponential Implementation
        y = (a * x) + b
        return y


@dataclass
class ModelSpecification:
    axes: tuple[str, str]
    model: Union[ExponentialModel, FixedExponentialModel, LinearIncreaseModel, LinearDecreaseModel]

    def get_x(self):
        return self.axes[0]

    def get_y(self):
        return self.axes[1]


def mapper(y: str, map_exponential: tuple[str], map_fixed: tuple[str], map_linear_increase: tuple[str],
           map_linear_decrease: tuple[str]) -> Union[ExponentialModel, FixedExponentialModel,
                                                     LinearIncreaseModel, LinearDecreaseModel]:
    if y in map_exponential:
        return ExponentialModel()
    elif y in map_fixed:
        return FixedExponentialModel()
    elif y in map_linear_decrease:
        return LinearDecreaseModel()
    elif y in map_linear_increase:
        return LinearIncreaseModel()
    else:
        pass


def set_up_fits(x_list: tuple[str] = ('time', 'coverage', 'pica', 'pgca', 'percent_coverage'),
                y_time_list: tuple[str] = ('activity', 'coverage', 'percent_coverage', 'pica', 'pgca',
                                           'p_plus_plus', 'p_plus_minus', 'p_plus_zero', 'p_zero_plus',
                                           'p_zero_zero', 'coverage', 'percent_coverage', 'pica', 'pgca',
                                           'p_plus_plus_given_plus', 'p_plus_minus_given_plus',
                                           'p_plus_zero_given_plus', 'p_zero_plus_given_zero',
                                           'p_zero_zero_given_zero', 'p_plus_plus_given_any',
                                           'p_plus_minus_given_any', 'p_plus_zero_given_any',
                                           'p_zero_plus_given_any', 'p_zero_zero_given_any'),
                y_other_list: tuple[str] = ('activity', 'p_plus_plus', 'p_plus_minus', 'p_plus_zero', 'p_zero_plus',
                                            'p_zero_zero', 'p_plus_plus_given_plus', 'p_plus_minus_given_plus',
                                            'p_plus_zero_given_plus', 'p_zero_plus_given_zero',
                                            'p_zero_zero_given_zero', 'p_plus_plus_given_any',
                                            'p_plus_minus_given_any', 'p_plus_zero_given_any',
                                            'p_zero_plus_given_any', 'p_zero_zero_given_any'),
                map_exponential: tuple[str] = ('activity', 'p_plus_plus', 'p_plus_plus_given_plus',
                                               'p_plus_plus_given_any', 'p_zero_plus', 'p_zero_plus_given_zero',
                                               'p_zero_plus_given_any'),
                map_fixed: tuple[str] = ('p_plus_minus', 'p_plus_minus_given_plus', 'p_plus_minus_given_any',
                                         'p_plus_zero', 'p_plus_zero_given_plus', 'p_plus_zero_given_any',
                                         'p_zero_zero', 'p_zero_zero_given_zero', 'p_zero_zero_given_any',
                                         'coverage', 'percent_coverage', 'pica', 'pgca'),
                map_linear_increase: tuple[str] = (),
                map_linear_decrease: tuple[str] = ()) -> dict[str, dict[str, ModelSpecification]]:
    xy_dict = {}
    for x in x_list:
        x_dict = {}
        if x == 'time':
            for y in y_time_list:
                x_dict[y] = ModelSpecification((x, y), mapper(y, map_exponential, map_fixed, map_linear_increase,
                                                              map_linear_decrease))
        else:
            for y in y_other_list:
                x_dict[y] = ModelSpecification((x, y), mapper(y, map_exponential, map_fixed, map_linear_increase,
                                                              map_linear_decrease))
        xy_dict[x] = x_dict
    return xy_dict

# TODO: Change the method of creating the xy dict so that it is easier for the user to pass in inputs
# keep it so that the xy dict is indexed first by x then by y to get a ModelSpecification
