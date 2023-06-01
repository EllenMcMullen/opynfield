from src.opynfield.config.defaults_settings import Defaults
from src.opynfield.config.user_input import UserInput
from src.opynfield.config.model_settings import ModelSpecification
from scipy.optimize import curve_fit
import pandas as pd
import numpy as np
import warnings


def fit_measure_by_time(group_individual_measure_df: pd.DataFrame, specs: ModelSpecification) -> pd.DataFrame:
    # rows are individuals and columns are time points
    # measure to be modeled by time
    params_list = []
    for i in range(group_individual_measure_df.shape[0]):
        # for each individual
        y_raw = group_individual_measure_df.iloc[i].values[1:].astype(float)
        x_raw = np.arange(group_individual_measure_df.shape[1]-1).astype(float)
        x_filter = x_raw[~np.isnan(y_raw)]
        y_filter = y_raw[~np.isnan(y_raw)]
        x = x_filter[~np.isnan(x_filter)]
        y = y_filter[~np.isnan(y_filter)]
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message='Covariance')
            try:
                # noinspection PyTupleAssignmentBalance
                params, cv = curve_fit(specs.model.model_function, x, y,
                                       p0=specs.model.initial_params, bounds=specs.model.bounds,
                                       **{'maxfev': specs.model.max_eval})
                params_list.append(pd.DataFrame(params))
            except ValueError:
                params = pd.DataFrame(np.ones(len(specs.model.initial_params),)*np.nan)
                params_list.append(params)
    params_df = pd.concat(params_list, axis=1).T
    # rows are individuals
    # columns are parameters
    return params_df


def fit_by_time(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], time_averaged_measures: list[str],
                model_params: dict[str, dict[str, ModelSpecification]]) -> dict[str, dict[str, pd.DataFrame]]:
    group_time_measure = {}
    for group in individual_measures_dfs:
        print(f'Fitting Models To Tracks From Group {group} by time')
        time_measure = {}
        for measure in time_averaged_measures:
            if measure != 'r':
                specs = model_params['time'][measure]
                m_params = fit_measure_by_time(individual_measures_dfs[group][measure], specs)
                time_measure[measure] = m_params
        group_time_measure[group] = time_measure
    # first dict key is group second dict key is measure
    # result is a df with rows as individuals and columns as parameters
    return group_time_measure


def fit_all(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], defaults: Defaults, user_inputs: UserInput,
            model_params: dict[str, dict[str, ModelSpecification]]):
    # dict[group] is a dict 2
    # dict 2[measure] is a df with rows as individuals and columns as time points
    group_time_measure = fit_by_time(individual_measures_dfs, defaults.time_averaged_measures, model_params)
    return group_time_measure
