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


def sort_by_coverage(coverages: pd.DataFrame, possible_coverage_values: np.ndarray,
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


def n_points_average(sorted_df: pd.DataFrame, n_points_coverage: int) -> pd.DataFrame:
    # figure out how many rows should be in the final dataframe
    lens_act = []
    for row in sorted_df['activity']:
        lens_act.append(len(row))
    n_points_total = sum(lens_act)
    n_rows = n_points_total / n_points_coverage
    # initialize results
    average_df = pd.DataFrame(np.ones(shape=(n_rows, len(sorted_df.columns))), columns=sorted_df.columns)
    for col in average_df:
        average_df[col] = average_df.apply(lambda x: [], axis = 1)
    # add items to lists to average

    return


def make_measures_by_coverage(group_individual_measures_dfs: dict[str, pd.DataFrame], defaults: Defaults):
    # pull the coverage values from all the individuals out
    coverages = group_individual_measures_dfs['coverage']
    # find the maximum coverage value reached by any fly in the group
    max_coverage = coverages.drop(columns=['Group']).max(axis=1, skipna=True).max(skipna=True)
    # create a list (rounded to 5 digits) of all the possible coverage values
    possible_coverage_values = np.round(np.linspace(0, max_coverage, int(max_coverage*360/defaults.node_size)), 5)
    # now we want to sort measure values into lists at each matching coverage value
    sorted_df = sort_by_coverage(coverages, possible_coverage_values, group_individual_measures_dfs,
                                 defaults.coverage_averaged_measures)
    # now we want to take every n points to average
    n_points_average(sorted_df, defaults.n_points_coverage)
    return


def coverage_average(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], defaults: Defaults,
                     user_inputs: UserInput):
    for group in individual_measures_dfs:
        # group_measures_by_coverage = \
        make_measures_by_coverage(individual_measures_dfs[group], defaults)
    return
