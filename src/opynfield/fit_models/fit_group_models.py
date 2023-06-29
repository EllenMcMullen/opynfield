import pandas as pd
import numpy as np
import warnings
from scipy.optimize import curve_fit
from opynfield.config.defaults_settings import Defaults
from opynfield.config.model_settings import ModelSpecification


def group_fit_measure_by_time(group_individual_measure_df: pd.DataFrame, specs: ModelSpecification,
                              uppers: pd.DataFrame, lowers: pd.DataFrame, initials: pd.DataFrame) -> pd.DataFrame:
    # rows are individuals and columns are time points
    # measure to be modeled by time
    # need to combine the coordinates from all the individuals to get 'group' coordinates
    y_raw = group_individual_measure_df.drop(columns=['Group']).values.flatten().astype(float)
    x_raw = np.tile(np.arange(group_individual_measure_df.shape[1] - 1).astype(float),
                    group_individual_measure_df.shape[0])
    x_filter = x_raw[~np.isnan(y_raw)]
    y_filter = y_raw[~np.isnan(y_raw)]
    x = x_filter[~np.isnan(x_filter)]
    y = y_filter[~np.isnan(x_filter)]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message='Covariance')
        # noinspection PyTupleAssignmentBalance
        params, cv = curve_fit(specs.model.model_function, x, y, p0=initials.values,
                               bounds=(lowers.values, uppers.values), **{'maxfev': specs.model.max_eval})
    return pd.DataFrame(params)


def group_fit_measure_by_cov_measure(group_individual_measure_df: pd.DataFrame, group_individual_cov_df: pd.DataFrame,
                                     specs: ModelSpecification, uppers: pd.DataFrame,
                                     lowers: pd.DataFrame, initials: pd.DataFrame) -> pd.DataFrame:
    # rows are individuals and columns are time points
    # measure to be modeled by time
    # need to combine the coordinates from all the individuals to get 'group' coordinates
    y_raw = group_individual_measure_df.drop(columns=['Group']).values.flatten().astype(float)
    x_raw = group_individual_cov_df.drop(columns=['Group']).values.flatten().astype(float)
    x_filter = x_raw[~np.isnan(y_raw)]
    y_filter = y_raw[~np.isnan(y_raw)]
    x = x_filter[~np.isnan(x_filter)]
    y = y_filter[~np.isnan(x_filter)]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message='Covariance')
        # noinspection PyTupleAssignmentBalance
        params, cv = curve_fit(specs.model.model_function, x, y, p0=initials.values,
                               bounds=(lowers.values, uppers.values), **{'maxfev': specs.model.max_eval})
    return pd.DataFrame(params)


def group_fit_by_time(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], time_averaged_measures: list[str],
                      model_params: dict[str, dict[str, ModelSpecification]], upper: dict[str, dict[str, pd.DataFrame]],
                      lower: dict[str, dict[str, pd.DataFrame]], initial: dict[str, dict[str, pd.DataFrame]],
                      group: str) -> dict[str, pd.DataFrame]:
    print(f'Fitting Models To Entire Group {group} by time')
    time_measures = {}
    for measure in time_averaged_measures:
        if measure != 'r':
            specs = model_params['time'][measure]
            m_params = group_fit_measure_by_time(individual_measures_dfs[group][measure], specs, upper['time'][measure],
                                                 lower['time'][measure], initial['time'][measure])
            time_measures[measure] = m_params
    # dict key is measure
    # result is a df with columns as parameters (only 1 row for the group's fit)
    return time_measures


def group_fit_by_cov_measure(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]],
                             coverage_averaged_measures: list[str],
                             model_params: dict[str, dict[str, ModelSpecification]], mode: str,
                             upper: dict[str, dict[str, pd.DataFrame]], lower: dict[str, dict[str, pd.DataFrame]],
                             initial: dict[str, dict[str, pd.DataFrame]], group: str) -> dict[str, pd.DataFrame]:
    print(f'Fitting Models To Entire Group {group} by {mode}')
    cov_measures = {}
    for measure in coverage_averaged_measures:
        specs = model_params[mode][measure]
        m_params = group_fit_measure_by_cov_measure(individual_measures_dfs[group][measure],
                                                    individual_measures_dfs[group][mode], specs,
                                                    upper[mode][measure], lower[mode][measure], initial[mode][measure])
        cov_measures[measure] = m_params
    # dict key is measure
    # result is a df with columns as parameters (only 1 row for the group's fit)
    return cov_measures


def group_fit_all(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], defaults: Defaults,
                  model_params: dict[str, dict[str, ModelSpecification]],
                  upper: dict[str, dict[str, dict[str, pd.DataFrame]]],
                  lower: dict[str, dict[str, dict[str, pd.DataFrame]]],
                  initial: dict[str, dict[str, dict[str, pd.DataFrame]]]) \
        -> dict[str, dict[str, dict[str, pd.DataFrame]]]:
    fits = {}
    for group in individual_measures_dfs:
        fits_group = {'time': group_fit_by_time(individual_measures_dfs, defaults.time_averaged_measures, model_params,
                                                upper[group], lower[group], initial[group], group),
                      'coverage': group_fit_by_cov_measure(individual_measures_dfs, defaults.coverage_averaged_measures,
                                                           model_params, 'coverage', upper[group], lower[group],
                                                           initial[group], group),
                      'pica': group_fit_by_cov_measure(individual_measures_dfs, defaults.coverage_averaged_measures,
                                                       model_params, 'pica', upper[group], lower[group], initial[group],
                                                       group),
                      'pgca': group_fit_by_cov_measure(individual_measures_dfs, defaults.coverage_averaged_measures,
                                                       model_params, 'pgca', upper[group], lower[group], initial[group],
                                                       group),
                      'percent_coverage': group_fit_by_cov_measure(individual_measures_dfs,
                                                                   defaults.coverage_averaged_measures, model_params,
                                                                   'percent_coverage', upper[group], lower[group],
                                                                   initial[group], group)
                      }
        fits[group] = fits_group
    return fits
