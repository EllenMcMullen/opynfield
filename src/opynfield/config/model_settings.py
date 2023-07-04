from dataclasses import dataclass
from typing import Union
import numpy as np


@dataclass()
class ExponentialModel:
    """This dataclass groups together relevant information for exponential model fits

    Attributes:
        initial_params (tuple[float, float, float): what p0 to use in curve fitting, defaults to (0.1, -0.1, 0.01)
        bounds (tuple[tuple[float, float, float], tuple[float, float, float]]): what bounds to use in curve fitting, defaults to ((0, -10, 0), (10, 0, 10))
        max_eval (int): max number of iterations the curve fitting process can take, defaults to 4000
        display_parts (tuple[str]): strings that when combined with parameter fit values will show the equation of the best fit model, defaults to ("y = ", " * e ^ (", " * x) + ")

    Methods:
        model_function: the exponential model function
    """
    initial_params: tuple[float, float, float] = (0.1, -0.1, 0.01)
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]] = (
        (0, -10, 0),
        (10, 0, 10),
    )
    max_eval: int = 4000
    display_parts: tuple[str] = ("y = ", " * e ^ (", " * x) + ")

    @staticmethod
    def model_function(x, a, b, c):
        # Exponential Implementation
        y = a * np.exp(b * x) + c
        return y


@dataclass()
class FixedExponentialModel:
    """This dataclass groups together relevant information for fixed exponential model fits

    Attributes:
        initial_params (tuple[float, float): what p0 to use in curve fitting, defaults to (-0.1, -0.1)
        bounds (tuple[tuple[float, float], tuple[float, float]]): what bounds to use in curve fitting, defaults to ((-10, -10), (0, 0))
        max_eval (int): max number of iterations the curve fitting process can take, defaults to 4000
        display_parts (tuple[str]): strings that when combined with parameter fit values will show the equation of the best fit model, defaults to ("y = ", " * (e ^ (", " * x) - 1)")

    Methods:
        model_function: the fixed exponential model function
    """
    initial_params: tuple[float, float] = (-0.1, -0.1)
    bounds: tuple[tuple[float, float], tuple[float, float]] = ((-10, -10), (0, 0))
    max_eval: int = 4000
    display_parts: tuple[str] = ("y = ", " * (e ^ (", " * x) - 1)")

    @staticmethod
    def model_function(x, a, b):
        # Exponential Implementation
        y = a * (np.exp(b * x) - 1)
        return y


@dataclass()
class LinearIncreaseModel:
    """This dataclass groups together relevant information for linear increase model fits

    Attributes:
        initial_params (tuple[float, float): what p0 to use in curve fitting, defaults to (0.1, 0.1)
        bounds (tuple[tuple[float, float], tuple[float, float]]): what bounds to use in curve fitting, defaults to ((0, 0), (10, 10))
        max_eval (int): max number of iterations the curve fitting process can take, defaults to 4000
        display_parts (tuple[str]): strings that when combined with parameter fit values will show the equation of the best fit model, defaults to ("y = ", " * x + ")

    Methods:
        model_function: the linear increase model function
    """
    initial_params: tuple[float, float] = (0.1, 0.1)
    bounds: tuple[tuple[float, float], tuple[float, float]] = ((0, 0), (10, 10))
    max_eval: int = 4000
    display_parts: tuple[str] = ("y = ", " * x + ")

    @staticmethod
    def model_function(x, a, b):
        # Exponential Implementation
        y = (a * x) + b
        return y


@dataclass()
class LinearDecreaseModel:
    """This dataclass groups together relevant information for linear decrease model fits

    Attributes:
        initial_params (tuple[float, float): what p0 to use in curve fitting, defaults to (-0.1, 0.1)
        bounds (tuple[tuple[float, float], tuple[float, float]]): what bounds to use in curve fitting, defaults to ((-10, 0), (0, 10))
        max_eval (int): max number of iterations the curve fitting process can take, defaults to 4000
        display_parts (tuple[str]): strings that when combined with parameter fit values will show the equation of the best fit model, defaults to ("y = ", " * x + ")

    Methods:
        model_function: the linear decrease model function
    """
    initial_params: tuple[float, float] = (-0.1, 0.1)
    bounds: tuple[tuple[float, float], tuple[float, float]] = ((-10, 0), (0, 10))
    max_eval: int = 4000
    display_parts: tuple[str] = ("y = ", " * x + ")

    @staticmethod
    def model_function(x, a, b):
        # Exponential Implementation
        y = (a * x) + b
        return y


@dataclass
class ModelSpecification:
    """This dataclass groups together a set of x and y axes to model the relationship between and the model (with
    associated model information) to use for that relationship

    Attributes:
        axes (tuple[str, str]): the x and y variables to model against each other
        model (Union[ExponentialModel, FixedExponentialModel, LinearIncreaseModel, LinearDecreaseModel]): the model to use to model the axes

    Methods:
        get_x: isolate the x-axis from the axes
        get_y: isolate the y-axis from the axes
    """
    axes: tuple[str, str]
    model: Union[
        ExponentialModel,
        FixedExponentialModel,
        LinearIncreaseModel,
        LinearDecreaseModel,
    ]

    def get_x(self):
        return self.axes[0]

    def get_y(self):
        return self.axes[1]


def mapper(
    y: str,
    map_exponential: tuple[str],
    map_fixed: tuple[str],
    map_linear_increase: tuple[str],
    map_linear_decrease: tuple[str],
) -> Union[
    ExponentialModel, FixedExponentialModel, LinearIncreaseModel, LinearDecreaseModel
]:
    """This function maps a y-axis variable to the model type that should be used in modeling its relationships

    :param y: the y-axis variable to map to a model type
    :type y: str
    :param map_exponential: which y-axis variables should be mapped to an exponential model
    :type map_exponential: tuple[str]
    :param map_fixed: which y-axis variables should be mapped to a fixed exponential model
    :type map_fixed: tuple[str]
    :param map_linear_increase: which y-axis variables should be mapped to a linear increase model
    :type map_linear_increase: tuple[str]
    :param map_linear_decrease: which y-axis variables should be mapped to a linear decrease model
    :type map_linear_decrease: tuple[str]
    :return: the model to use
    :rtype: Union[ExponentialModel, FixedExponentialModel, LinearIncreaseModel, LinearDecreaseModel]
    """
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


def set_up_fits(
    x_list: tuple[str] = ("time", "coverage", "pica", "pgca", "percent_coverage"),
    y_time_list: tuple[str] = (
        "activity",
        "coverage",
        "percent_coverage",
        "pica",
        "pgca",
        "p_plus_plus",
        "p_plus_minus",
        "p_plus_zero",
        "p_zero_plus",
        "p_zero_zero",
        "coverage",
        "percent_coverage",
        "pica",
        "pgca",
        "p_plus_plus_given_plus",
        "p_plus_minus_given_plus",
        "p_plus_zero_given_plus",
        "p_zero_plus_given_zero",
        "p_zero_zero_given_zero",
        "p_plus_plus_given_any",
        "p_plus_minus_given_any",
        "p_plus_zero_given_any",
        "p_zero_plus_given_any",
        "p_zero_zero_given_any"
    ),
    y_other_list: tuple[str] = (
        "activity",
        "p_plus_plus",
        "p_plus_minus",
        "p_plus_zero",
        "p_zero_plus",
        "p_zero_zero",
        "p_plus_plus_given_plus",
        "p_plus_minus_given_plus",
        "p_plus_zero_given_plus",
        "p_zero_plus_given_zero",
        "p_zero_zero_given_zero",
        "p_plus_plus_given_any",
        "p_plus_minus_given_any",
        "p_plus_zero_given_any",
        "p_zero_plus_given_any",
        "p_zero_zero_given_any"
    ),
    map_exponential: tuple[str] = (
        "activity",
        "p_plus_plus",
        "p_plus_plus_given_plus",
        "p_plus_plus_given_any",
        "p_zero_plus",
        "p_zero_plus_given_zero",
        "p_zero_plus_given_any"
    ),
    map_fixed: tuple[str] = (
        "p_plus_minus",
        "p_plus_minus_given_plus",
        "p_plus_minus_given_any",
        "p_plus_zero",
        "p_plus_zero_given_plus",
        "p_plus_zero_given_any",
        "p_zero_zero",
        "p_zero_zero_given_zero",
        "p_zero_zero_given_any",
        "coverage",
        "percent_coverage",
        "pica",
        "pgca",
    ),
    map_linear_increase: tuple[str] = (),
    map_linear_decrease: tuple[str] = (),
) -> dict[str, dict[str, ModelSpecification]]:
    """This function

    :param x_list: the x-axis variables, defaults to ("time", "coverage", "pica", "pgca", "percent_coverage")
    :type x_list: tuple[str]
    :param y_time_list: the y-axis variables that can be mapped against time, defaults to ("activity", "coverage", "percent_coverage", "pica", "pgca", "p_plus_plus", "p_plus_minus", "p_plus_zero", "p_zero_plus", "p_zero_zero", "coverage", "percent_coverage", "pica", "pgca", "p_plus_plus_given_plus", "p_plus_minus_given_plus", "p_plus_zero_given_plus", "p_zero_plus_given_zero", "p_zero_zero_given_zero", "p_plus_plus_given_any", "p_plus_minus_given_any", "p_plus_zero_given_any", "p_zero_plus_given_any", "p_zero_zero_given_any")
    :type y_time_list: tuple[str]
    :param y_other_list: the y-axis variables that can be mapped against coverage measures, defaults to ("activity", "p_plus_plus", "p_plus_minus", "p_plus_zero", "p_zero_plus", "p_zero_zero", "p_plus_plus_given_plus", "p_plus_minus_given_plus", "p_plus_zero_given_plus", "p_zero_plus_given_zero", "p_zero_zero_given_zero", "p_plus_plus_given_any", "p_plus_minus_given_any", "p_plus_zero_given_any", "p_zero_plus_given_any", "p_zero_zero_given_any")
    :type y_other_list: tuple[str]
    :param map_exponential: the y-axis variables that should be modeled with an exponential model, defaults to ("activity", "p_plus_plus", "p_plus_plus_given_plus", "p_plus_plus_given_any", "p_zero_plus", "p_zero_plus_given_zero", "p_zero_plus_given_any",)
    :type map_exponential:  tuple[str]
    :param map_fixed: the y-axis variables that should be modeled with a fixed exponential model, defaults to ("p_plus_minus", "p_plus_minus_given_plus", "p_plus_minus_given_any", "p_plus_zero", "p_plus_zero_given_plus", "p_plus_zero_given_any", "p_zero_zero", "p_zero_zero_given_zero", "p_zero_zero_given_any", "coverage", "percent_coverage", "pica", "pgca",)
    :type map_fixed: tuple[str]
    :param map_linear_increase: the y-axis variables that should be modeled with a linear increase model, defaults to ()
    :type map_linear_increase: tuple[str]
    :param map_linear_decrease: the y-axis variables that should be modeled with a linear decrease model, defaults to ()
    :type map_linear_decrease: tuple[str]
    :return: a dictionary of x-axis to a dictionary of y-axis to a model type to use
    :rtype: dict[str, dict[str, ModelSpecification]]
    """
    xy_dict = {}
    for x in x_list:
        x_dict = {}
        if x == "time":
            for y in y_time_list:
                x_dict[y] = ModelSpecification(
                    (x, y),
                    mapper(
                        y,
                        map_exponential,
                        map_fixed,
                        map_linear_increase,
                        map_linear_decrease,
                    ),
                )
        else:
            for y in y_other_list:
                x_dict[y] = ModelSpecification(
                    (x, y),
                    mapper(
                        y,
                        map_exponential,
                        map_fixed,
                        map_linear_increase,
                        map_linear_decrease,
                    ),
                )
        xy_dict[x] = x_dict
    return xy_dict


# TODO: Change the method of creating the xy dict so that it is easier for the user to pass in inputs
# keep it so that the xy dict is indexed first by x then by y to get a ModelSpecification
