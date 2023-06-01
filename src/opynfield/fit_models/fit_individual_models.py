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
        x_raw = np.arange(group_individual_measure_df.shape[1] - 1).astype(float)
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
                params = pd.DataFrame(np.ones(len(specs.model.initial_params), ) * np.nan)
                params_list.append(params)
    params_df = pd.concat(params_list, axis=1).T
    # rows are individuals
    # columns are parameters
    return params_df


def fit_measure_by_cov(group_individual_measure_df: pd.DataFrame, group_individual_cov_df: pd.DataFrame,
                       specs: ModelSpecification) -> pd.DataFrame:
    # rows are individuals and columns are time points
    # measure to be modeled by mode
    params_list = []
    for i in range(group_individual_measure_df.shape[0]):
        # for each individual
        y_raw = group_individual_measure_df.iloc[i].values[1:].astype(float)
        x_raw = group_individual_cov_df.iloc[i].values[1:].astype(float)
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
                params = pd.DataFrame(np.ones(len(specs.model.initial_params), ) * np.nan)
                params_list.append(params)
    params_df = pd.concat(params_list, axis=1).T
    # rows are individuals
    # columns are parameters
    return params_df


def fit_by_time(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], time_averaged_measures: list[str],
                model_params: dict[str, dict[str, ModelSpecification]], group: str) -> dict[str, pd.DataFrame]:
    print(f'Fitting Models To Tracks From Group {group} by time')
    time_measures = {}
    for measure in time_averaged_measures:
        if measure != 'r':
            specs = model_params['time'][measure]
            m_params = fit_measure_by_time(individual_measures_dfs[group][measure], specs)
            time_measures[measure] = m_params
    # dict key is measure
    # result is a df with rows as individuals and columns as parameters
    return time_measures


def fit_by_cov_measure(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]],
                       coverage_averaged_measures: list[str], model_params: dict[str, dict[str, ModelSpecification]],
                       mode: str, group: str) -> dict[str, pd.DataFrame]:
    print(f'Fitting Models To Tracks From Group {group} by {mode}')
    cov_measures = {}
    for measure in coverage_averaged_measures:
        specs = model_params[mode][measure]
        m_params = fit_measure_by_cov(individual_measures_dfs[group][mode],
                                      individual_measures_dfs[group][measure], specs)
        cov_measures[measure] = m_params
    # dict key is measure
    # result is a df with rows as individuals and columns as parameters
    return cov_measures


def fit_all(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], defaults: Defaults,
            model_params: dict[str, dict[str, ModelSpecification]]) -> dict[str, dict[str, dict[str, pd.DataFrame]]]:
    # dict[group] is a dict 2
    # dict 2[measure] is a df with rows as individuals and columns as time points
    # returns a dict of [group] -> dict[x-axis] -> dict[measure] -> df
    fits = {}
    for group in individual_measures_dfs:
        fits_group = {'time': fit_by_time(individual_measures_dfs, defaults.time_averaged_measures, model_params,
                                          group),
                      'coverage': fit_by_cov_measure(individual_measures_dfs, defaults.coverage_averaged_measures,
                                                     model_params, 'coverage', group),
                      'pica': fit_by_cov_measure(individual_measures_dfs, defaults.coverage_averaged_measures,
                                                 model_params, 'pica', group),
                      'pgca': fit_by_cov_measure(individual_measures_dfs, defaults.coverage_averaged_measures,
                                                 model_params, 'pgca', group),
                      'percent_coverage': fit_by_cov_measure(individual_measures_dfs,
                                                             defaults.coverage_averaged_measures, model_params,
                                                             'percent_coverage', group)
                      }
        fits[group] = fits_group
    return fits


def find_fit_bounds(fits: dict[str, dict[str, dict[str, pd.DataFrame]]],
                    user_inputs: UserInput) -> tuple[dict[str, dict[str, dict[str, pd.DataFrame]]],
                                                     dict[str, dict[str, dict[str, pd.DataFrame]]],
                                                     dict[str, dict[str, dict[str, pd.DataFrame]]]]:
    # dict of[group] -> dict of [x-axis] -> dict[measure] -> df
    upper_group_x_measure_dict = {}
    lower_group_x_measure_dict = {}
    mean_group_x_measure_dict = {}
    for group in fits:
        upper_x_measure_dict = {}
        lower_x_measure_dict = {}
        mean_x_measure_dict = {}
        for x_axis in fits[group]:
            upper_measure_dict = {}
            lower_measure_dict = {}
            mean_measure_dict = {}
            for measure in fits[group][x_axis]:
                df = fits[group][x_axis][measure]
                m = df.mean()
                s = df.std() * user_inputs.bound_level
                lower = m - s
                upper = m + s
                for i in range(len(upper)):
                    if np.sign(lower[i]) != np.sign(m[i]):
                        lower[i] = 0
                        # if they don't match signs -> move bound to 0
                        # if they do match signs -> keep the bound as is
                    if np.sign(upper[i]) != np.sign(m[i]):
                        upper[i] = 0
                        # if they don't match signs -> move bound to 0
                        # if they do match signs -> keep the bound as is
                upper_measure_dict[measure] = upper
                lower_measure_dict[measure] = lower
                mean_measure_dict[measure] = m
            upper_x_measure_dict[x_axis] = upper_measure_dict
            lower_x_measure_dict[x_axis] = lower_measure_dict
            mean_x_measure_dict[x_axis] = mean_measure_dict
        upper_group_x_measure_dict[group] = upper_x_measure_dict
        lower_group_x_measure_dict[group] = lower_x_measure_dict
        mean_group_x_measure_dict[group] = mean_x_measure_dict
    return upper_group_x_measure_dict, lower_group_x_measure_dict, mean_group_x_measure_dict


def re_fit_measure_by_time(group_individual_measure_df: pd.DataFrame, specs: ModelSpecification,
                           uppers: pd.DataFrame, lowers: pd.DataFrame, initials: pd.DataFrame) -> pd.DataFrame:
    # rows are individuals and columns are time points
    # measure to be modeled by time
    params_list = []
    for i in range(group_individual_measure_df.shape[0]):
        # for each individual
        y_raw = group_individual_measure_df.iloc[i].values[1:].astype(float)
        x_raw = np.arange(group_individual_measure_df.shape[1] - 1).astype(float)
        x_filter = x_raw[~np.isnan(y_raw)]
        y_filter = y_raw[~np.isnan(y_raw)]
        x = x_filter[~np.isnan(x_filter)]
        y = y_filter[~np.isnan(y_filter)]
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message='Covariance')
            try:
                # noinspection PyTupleAssignmentBalance
                params, cv = curve_fit(specs.model.model_function, x, y,
                                       p0=initials.values, bounds=(lowers.values, uppers.values),
                                       **{'maxfev': specs.model.max_eval})
                params_list.append(pd.DataFrame(params))
            except ValueError:
                params = pd.DataFrame(np.ones(len(specs.model.initial_params), ) * np.nan)
                params_list.append(params)
    params_df = pd.concat(params_list, axis=1).T
    # rows are individuals
    # columns are parameters
    return params_df


def re_fit_by_time(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], time_averaged_measures: list[str],
                   model_params: dict[str, dict[str, ModelSpecification]], upper: dict[str, dict[str, pd.DataFrame]],
                   lower: dict[str, dict[str, pd.DataFrame]], initial: dict[str, dict[str, pd.DataFrame]], group: str):
    print(f'Re-Fitting Models To Tracks From Group {group} by time')
    time_measures = {}
    for measure in time_averaged_measures:
        if measure != 'r':
            specs = model_params['time'][measure]
            m_params = re_fit_measure_by_time(individual_measures_dfs[group][measure], specs,
                                              upper['time'][measure], lower['time'][measure], initial['time'][measure])
            time_measures[measure] = m_params
    # dict key is measure
    # result is a dy with rows as individuals and columns as parameters
    return time_measures


def re_fit_measure_by_cov_measure(group_individual_measure_df: pd.DataFrame, group_individual_cov_df: pd.DataFrame,
                                  specs: ModelSpecification, uppers: pd.DataFrame,
                                  lowers: pd.DataFrame, initials: pd.DataFrame) -> pd.DataFrame:
    # rows are individuals and columns are time points
    # measure to be modeled by time
    params_list = []
    for i in range(group_individual_measure_df.shape[0]):
        # for each individual
        y_raw = group_individual_measure_df.iloc[i].values[1:].astype(float)
        x_raw = group_individual_cov_df.iloc[i].values[1:].astype(float)
        x_filter = x_raw[~np.isnan(y_raw)]
        y_filter = y_raw[~np.isnan(y_raw)]
        x = x_filter[~np.isnan(x_filter)]
        y = y_filter[~np.isnan(y_filter)]
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message='Covariance')
            try:
                # noinspection PyTupleAssignmentBalance
                params, cv = curve_fit(specs.model.model_function, x, y,
                                       p0=initials.values, bounds=(lowers.values, uppers.values),
                                       **{'maxfev': specs.model.max_eval})
            except ValueError:
                params = np.ones(len(specs.model.initial_params), ) * np.nan
        params_list.append(pd.DataFrame(params))
    params_df = pd.concat(params_list, axis=1).T
    # rows are individuals
    # columns are parameters
    return params_df


def re_fit_by_cov_measure(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]],
                          coverage_averaged_measures: list[str],
                          model_params: dict[str, dict[str, ModelSpecification]], mode: str,
                          upper: dict[str, dict[str, pd.DataFrame]], lower: dict[str, dict[str, pd.DataFrame]],
                          initial: dict[str, dict[str, pd.DataFrame]],
                          group: str):
    print(f'Re-Fitting Models To Tracks From Group {group} by {mode}')
    cov_measures = {}
    for measure in coverage_averaged_measures:
        specs = model_params[mode][measure]
        m_params = re_fit_measure_by_cov_measure(individual_measures_dfs[group][measure],
                                                 individual_measures_dfs[group][measure], specs,
                                                 upper[mode][measure], lower[mode][measure], initial[mode][measure])
        cov_measures[measure] = m_params
    # dict key is measure
    # result is a df with rows as individuals and columns as parameters
    return cov_measures


def re_fit_all(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], defaults: Defaults,
               model_params: dict[str, dict[str, ModelSpecification]],
               upper: dict[str, dict[str, dict[str, pd.DataFrame]]],
               lower: dict[str, dict[str, dict[str, pd.DataFrame]]],
               initial: dict[str, dict[str, dict[str, pd.DataFrame]]]) -> dict[str, dict[str, dict[str, pd.DataFrame]]]:
    fits = {}
    for group in individual_measures_dfs:
        fits_group = {'time': re_fit_by_time(individual_measures_dfs, defaults.time_averaged_measures, model_params,
                                             upper[group], lower[group], initial[group], group),
                      'coverage': re_fit_by_cov_measure(individual_measures_dfs, defaults.coverage_averaged_measures,
                                                        model_params, 'coverage', upper[group], lower[group],
                                                        initial[group], group),
                      'pica': re_fit_by_cov_measure(individual_measures_dfs, defaults.coverage_averaged_measures,
                                                    model_params, 'pica', upper[group], lower[group], initial[group],
                                                    group),
                      'pgca': re_fit_by_cov_measure(individual_measures_dfs, defaults.coverage_averaged_measures,
                                                    model_params, 'pgca', upper[group], lower[group], initial[group],
                                                    group),
                      'percent_coverage': re_fit_by_cov_measure(individual_measures_dfs,
                                                                defaults.coverage_averaged_measures, model_params,
                                                                'percent_coverage', upper[group], lower[group],
                                                                initial[group], group)
                      }
        fits[group] = fits_group
    return fits
