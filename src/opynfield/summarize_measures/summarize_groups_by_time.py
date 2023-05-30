import warnings
import numpy as np
from src.opynfield.config.defaults_settings import Defaults
from src.opynfield.config.user_input import UserInput
import pandas as pd
import os


def time_average(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], defaults: Defaults,
                 user_inputs: UserInput) -> dict[str, dict[str, pd.DataFrame]]:
    # for all the groups
    group_avg_dfs = {}
    for group in individual_measures_dfs:
        # for all the measures of that group
        g_avg_dfs = {}
        for measure in individual_measures_dfs[group]:
            if measure in defaults.time_averaged_measures:
                # remove group name
                df_to_avg = individual_measures_dfs[group][measure].drop(columns=['Group'])
                # get measure time average
                measure_mean = pd.DataFrame(df_to_avg.mean(axis=0, skipna=True)).T
                # get measure time SEM
                measure_sem = pd.DataFrame(df_to_avg.sem(axis=0, skipna=True, ddof=1)).T
                # combine them into one result df and save to that group
                mean_sem = pd.concat([measure_mean, measure_sem])
                mean_sem.insert(0, "Which", ['Mean', 'SEM'])  # noqa
                g_avg_dfs[measure] = mean_sem
        # save that group to all the groups
        group_avg_dfs[group] = g_avg_dfs
    # we have a dict with a dict for each group with each measure's avg df
    if defaults.save_group_csvs:
        # save the dfs
        for group in group_avg_dfs:
            path = user_inputs.result_path + '/Groups/' + user_inputs.groups_to_paths[group] + '/AverageMeasures'
            os.makedirs(path, exist_ok=True)
            for df_key in group_avg_dfs[group]:
                df_path = path + '/TimeAverage_' + df_key + '.csv'
                group_avg_dfs[group][df_key].to_csv(path_or_buf=df_path, index=False)
    if defaults.save_all_group_csvs:
        # add group names to group dfs, then concat the dfs from each group together to make one
        combined_avg_dfs = {}
        # for each measure
        for measure in group_avg_dfs[group]:  # noqa
            # pull that measure from each group
            m_list = []
            for g in group_avg_dfs:
                ga_df = group_avg_dfs[g][measure]
                ga_df.insert(0, "Group", g)
                m_list.append(ga_df)
            # combine them into one df
            combined_avg_dfs[measure] = pd.concat(m_list)
        path = user_inputs.result_path + '/Groups/CombinedGroups/AverageMeasures'
        os.makedirs(path, exist_ok=True)
        for df_key in combined_avg_dfs:
            df_path = path + '/CombinedGroups_TimeAverage_' + df_key + '.csv'
            combined_avg_dfs[df_key].to_csv(path_or_buf=df_path, index=False)
            # save csv for the combined group
    return group_avg_dfs


def pair_to_coverage(group_measures_dict: dict[str, pd.DataFrame],
                     response_measures: list[str]) -> tuple[pd.DataFrame, list[str]]:
    # set up a df with possible coverage values and empty lists
    measures = response_measures[:]
    measures.insert(0, 'coverage')
    pre_sorted_values = pd.DataFrame()
    for measure in measures:
        pre_sorted_values[measure] = group_measures_dict[measure].drop(columns='Group').values.flatten(order='C')
    return pre_sorted_values, measures


def pair_to_pica(group_measures_dict: dict[str, pd.DataFrame],
                 response_measures: list[str]) -> tuple[pd.DataFrame, list[str]]:
    # set up a df with possible coverage values and empty lists
    measures = response_measures[:]
    measures.insert(0, 'pica')
    pre_sorted_values = pd.DataFrame()
    for measure in measures:
        pre_sorted_values[measure] = group_measures_dict[measure].drop(columns='Group').values.flatten(order='C')
    return pre_sorted_values, measures


def pair_to_pgca(group_measures_dict: dict[str, pd.DataFrame],
                 response_measures: list[str]) -> tuple[pd.DataFrame, list[str]]:
    # set up a df with possible coverage values and empty lists
    measures = response_measures[:]
    measures.insert(0, 'pgca')
    pre_sorted_values = pd.DataFrame()
    for measure in measures:
        pre_sorted_values[measure] = group_measures_dict[measure].drop(columns='Group').values.flatten(order='C')
    return pre_sorted_values, measures


def sort_by_coverage(possible_coverage_values: np.ndarray,
                     group_measures_dict: dict[str, pd.DataFrame],
                     response_measures: list[str]) -> pd.DataFrame:
    # pair up measures and the coverage they occurred at
    pre_sorted_values, measures = pair_to_coverage(group_measures_dict, response_measures)
    # set up a df with possible coverage values and empty lists
    sorted_values = pd.DataFrame()
    for measure in measures:
        if measure == 'coverage':
            sorted_values[measure] = possible_coverage_values
        else:
            sorted_values[measure] = sorted_values.apply(lambda x: [], axis=1)
    # then iterate through pre_sorted_values rows and append measures to lists
    for ind in pre_sorted_values.index:
        c_index = np.argmin(np.abs(pre_sorted_values['coverage'][ind] - possible_coverage_values))
        for m in response_measures:
            sorted_values[m][c_index].append(pre_sorted_values[m][ind])
    return sorted_values


def sort_by_pica(possible_pica_values: np.ndarray, group_measures_dict: dict[str, pd.DataFrame],
                 response_measures: list[str]) -> pd.DataFrame:
    # pair up measures and the pica they occurred at
    pre_sorted_values, measures = pair_to_pica(group_measures_dict, response_measures)
    # set up a df with possible coverage values and empty lists
    sorted_values = pd.DataFrame()
    for measure in measures:
        if measure == 'pica':
            sorted_values[measure] = possible_pica_values
        else:
            sorted_values[measure] = sorted_values.apply(lambda x: [], axis=1)
    # then iterate through pre_sorted_values rows and append measures to lists
    for ind in pre_sorted_values.index:
        c_index = np.argmin(np.abs(pre_sorted_values['pica'][ind] - possible_pica_values))
        for m in response_measures:
            sorted_values[m][c_index].append(pre_sorted_values[m][ind])
    return sorted_values


def sort_by_pgca(possible_pgca_values: np.ndarray, group_measures_dict: dict[str, pd.DataFrame],
                 response_measures: list[str]) -> pd.DataFrame:
    # pair up measures and the pica they occurred at
    pre_sorted_values, measures = pair_to_pgca(group_measures_dict, response_measures)
    # set up a df with possible coverage values and empty lists
    sorted_values = pd.DataFrame()
    for measure in measures:
        if measure == 'pgca':
            sorted_values[measure] = possible_pgca_values
        else:
            sorted_values[measure] = sorted_values.apply(lambda x: [], axis=1)
    # then iterate through pre_sorted_values rows and append measures to lists
    for ind in pre_sorted_values.index:
        c_index = np.argmin(np.abs(pre_sorted_values['pgca'][ind] - possible_pgca_values))
        for m in response_measures:
            sorted_values[m][c_index].append(pre_sorted_values[m][ind])
    return sorted_values


def n_points_average_coverage(sorted_df: pd.DataFrame, n_points_coverage: int,
                              base_column: str = 'coverage') -> pd.DataFrame:
    response_columns = [item for item in sorted_df.columns if item != base_column]
    exploded_df = sorted_df.explode(response_columns)
    dummy_col = 'grouping'
    exploded_df[dummy_col] = np.repeat(range(int(1+len(exploded_df)/n_points_coverage)),
                                       n_points_coverage)[:len(exploded_df)]
    for_average = exploded_df.groupby(dummy_col).agg({c: list for c in response_columns} | {base_column: list})
    ready_for_average = for_average.reset_index().drop(columns=dummy_col)
    return ready_for_average


def n_points_average_pica(sorted_df: pd.DataFrame, n_points_pica: int,
                          base_column: str = 'pica') -> pd.DataFrame:
    response_columns = [item for item in sorted_df.columns if item != base_column]
    exploded_df = sorted_df.explode(response_columns)
    dummy_col = 'grouping'
    exploded_df[dummy_col] = np.repeat(range(int(1+len(exploded_df)/n_points_pica)),
                                       n_points_pica)[:len(exploded_df)]
    for_average = exploded_df.groupby(dummy_col).agg({c: list for c in response_columns} | {base_column: list})
    ready_for_average = for_average.reset_index().drop(columns=dummy_col)
    return ready_for_average


def n_points_average_pgca(sorted_df: pd.DataFrame, n_points_pica: int,
                          base_column: str = 'pgca') -> pd.DataFrame:
    response_columns = [item for item in sorted_df.columns if item != base_column]
    exploded_df = sorted_df.explode(response_columns)
    dummy_col = 'grouping'
    exploded_df[dummy_col] = np.repeat(range(int(1+len(exploded_df)/n_points_pica)),
                                       n_points_pica)[:len(exploded_df)]
    for_average = exploded_df.groupby(dummy_col).agg({c: list for c in response_columns} | {base_column: list})
    ready_for_average = for_average.reset_index().drop(columns=dummy_col)
    return ready_for_average


def average_points(ready_for_average: pd.DataFrame) -> pd.DataFrame:
    coverage_averages = pd.DataFrame()
    for col in ready_for_average:
        col_avg = col + ' mean'
        col_sem = col + ' sem'
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            coverage_averages[col_avg] = ready_for_average[col].apply(lambda x: np.nanmean(x))
            std = ready_for_average[col].apply(lambda x: np.nanstd(x))
            count = ready_for_average[col].apply(lambda x: np.count_nonzero(~np.isnan(x)))
            coverage_averages[col_sem] = std/np.sqrt(count)
    return coverage_averages


def make_measures_by_coverage(group_individual_measures_dfs: dict[str, pd.DataFrame], defaults: Defaults):
    # pull the coverage values from all the individuals out
    coverages = group_individual_measures_dfs['coverage']
    # find the maximum coverage value reached by any fly in the group
    max_coverage = coverages.drop(columns=['Group']).max(axis=1, skipna=True).max(skipna=True)
    # create a list (rounded to 5 digits) of all the possible coverage values
    possible_coverage_values = np.round(np.linspace(0, max_coverage, int(max_coverage*360/defaults.node_size)), 5)
    # now we want to sort measure values into lists at each matching coverage value
    sorted_df = sort_by_coverage(possible_coverage_values, group_individual_measures_dfs,
                                 defaults.coverage_averaged_measures)
    # now we want to take every n points to average
    ready_for_average = n_points_average_coverage(sorted_df, defaults.n_points_coverage)
    # then actually average the n points
    coverage_averages = average_points(ready_for_average)
    return coverage_averages


def make_measures_by_pica(group_individual_measures_dfs: dict[str, pd.DataFrame], defaults: Defaults):
    # pull the coverage values from all the individuals out
    picas = group_individual_measures_dfs['pica']
    # find the maximum coverage value reached by any fly in the group
    max_pica = picas.drop(columns=['Group']).max(axis=1, skipna=True).max(skipna=True)
    # create a list (rounded to 5 digits) of all the possible coverage values
    possible_pica_values = np.round(np.linspace(0, max_pica, 2000), 5)
    # now we want to sort measure values into lists at each matching coverage value
    sorted_df = sort_by_pica(possible_pica_values, group_individual_measures_dfs,
                             defaults.coverage_averaged_measures)
    # now we want to take every n points to average
    ready_for_average = n_points_average_pica(sorted_df, defaults.n_points_pica)
    # then actually average the n points
    pica_averages = average_points(ready_for_average)
    return pica_averages


def make_measures_by_pgca(group_individual_measures_dfs: dict[str, pd.DataFrame], defaults: Defaults):
    # pull the coverage values from all the individuals out
    pgcas = group_individual_measures_dfs['pgca']
    # find the maximum coverage value reached by any fly in the group
    max_pgca = pgcas.drop(columns=['Group']).max(axis=1, skipna=True).max(skipna=True)
    # create a list (rounded to 5 digits) of all the possible coverage values
    possible_pgca_values = np.round(np.linspace(0, max_pgca, 2000), 5)
    # now we want to sort measure values into lists at each matching coverage value
    sorted_df = sort_by_pgca(possible_pgca_values, group_individual_measures_dfs,
                             defaults.coverage_averaged_measures)
    # now we want to take every n points to average
    ready_for_average = n_points_average_pgca(sorted_df, defaults.n_points_pgca)
    # then actually average the n points
    pgca_averages = average_points(ready_for_average)
    return pgca_averages


def coverage_average(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]],
                     defaults: Defaults) -> dict[str, pd.DataFrame]:
    group_measures_by_coverage = {}
    for group in individual_measures_dfs:
        group_measures_by_coverage[group] = make_measures_by_coverage(individual_measures_dfs[group], defaults)
    return group_measures_by_coverage


def pica_average(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]],
                 defaults: Defaults) -> dict[str, pd.DataFrame]:
    group_measures_by_pica = {}
    for group in individual_measures_dfs:
        group_measures_by_pica[group] = make_measures_by_pica(individual_measures_dfs[group], defaults)
    return group_measures_by_pica


def pgca_average(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]],
                 defaults: Defaults) -> dict[str, pd.DataFrame]:
    group_measures_by_pgca = {}
    for group in individual_measures_dfs:
        group_measures_by_pgca[group] = make_measures_by_pgca(individual_measures_dfs[group], defaults)
    return group_measures_by_pgca
