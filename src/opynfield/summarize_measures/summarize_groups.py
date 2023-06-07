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
        print(f'Averaging Tracks From Group {group} by time')
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


def pair_to_cov_measure(group_measures_dict: dict[str, pd.DataFrame],
                        response_measures: list[str], mode: str) -> tuple[pd.DataFrame, list[str]]:
    # set up a df with possible coverage values and empty lists
    measures = response_measures[:]
    measures.insert(0, mode)
    pre_sorted_values = pd.DataFrame()
    for measure in measures:
        pre_sorted_values[measure] = group_measures_dict[measure].drop(columns='Group').values.flatten(order='C')
    return pre_sorted_values, measures


def sort_by_cov_measure(possible_coverage_values: np.ndarray, group_measures_dict: dict[str, pd.DataFrame],
                        response_measures: list[str], mode: str) -> pd.DataFrame:
    # pair up measures and the coverage they occurred at
    pre_sorted_values, measures = pair_to_cov_measure(group_measures_dict, response_measures, mode)
    # set up a df with possible coverage values and empty lists
    sorted_values = pd.DataFrame()
    for measure in measures:
        if measure == mode:
            sorted_values[measure] = possible_coverage_values
        else:
            sorted_values[measure] = sorted_values.apply(lambda x: [], axis=1)
    # then iterate through pre_sorted_values rows and append measures to lists
    for ind in pre_sorted_values.index:
        c_index = np.argmin(np.abs(pre_sorted_values[mode][ind] - possible_coverage_values))
        for m in response_measures:
            sorted_values[m][c_index].append(pre_sorted_values[m][ind])
    return sorted_values


def n_points_average_cov_measure(sorted_df: pd.DataFrame, n_points: int,
                                 mode: str) -> pd.DataFrame:
    response_columns = [item for item in sorted_df.columns if item != mode]
    exploded_df = sorted_df.explode(response_columns)
    dummy_col = 'grouping'
    exploded_df[dummy_col] = np.repeat(range(int(1 + len(exploded_df) / n_points)),
                                       n_points)[:len(exploded_df)]
    for_average = exploded_df.groupby(dummy_col).agg({c: list for c in response_columns} | {mode: list})
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


def make_measures_by_cov_measure(group_individual_measures_dfs: dict[str, pd.DataFrame],
                                 defaults: Defaults, mode: str) -> pd.DataFrame:
    # pull the coverage values from all the individuals out
    coverages = group_individual_measures_dfs[mode]
    # find the maximum coverage value reached by any fly in the group
    max_coverage = coverages.drop(columns=['Group']).max(axis=1, skipna=True).max(skipna=True)
    # create a list (rounded to 5 digits) of all the possible coverage values
    if mode == 'coverage':
        possible_coverage_values = np.round(np.linspace(0, max_coverage, int(max_coverage * 360 / defaults.node_size)),
                                            5)
    else:
        possible_coverage_values = np.round(np.linspace(0, max_coverage, 2000), 5)
    # now we want to sort measure values into lists at each matching coverage value
    sorted_df = sort_by_cov_measure(possible_coverage_values, group_individual_measures_dfs,
                                    defaults.coverage_averaged_measures, mode)
    # now we want to take every n points to average
    if mode == 'coverage':
        n_points = defaults.n_points_coverage
    elif mode == 'pica':
        n_points = defaults.n_points_pica
    else:
        n_points = defaults.n_points_pgca
    ready_for_average = n_points_average_cov_measure(sorted_df, n_points, mode)
    # then actually average the n points
    coverage_averages = average_points(ready_for_average)
    return coverage_averages


def cov_measure_average(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], defaults: Defaults,
                        user_inputs: UserInput, mode: str) -> dict[str, pd.DataFrame]:
    group_measures_by_coverage = {}
    for group in individual_measures_dfs:
        print(f'Averaging Tracks From Group {group} By {mode}')
        group_measures_by_coverage[group] = make_measures_by_cov_measure(individual_measures_dfs[group], defaults, mode)
    # have a dict of group name -> df with all measures
    if defaults.save_group_csvs:
        df_group_dict = {}
        cov_avg = mode + ' mean'
        cov_sem = mode + ' sem'
        for group in group_measures_by_coverage:
            group_dict = {}
            path = user_inputs.result_path + '/Groups/' + user_inputs.groups_to_paths[group] + '/AverageMeasures'
            os.makedirs(path, exist_ok=True)
            for measure in defaults.coverage_averaged_measures:
                m_avg = measure + ' mean'
                m_sem = measure + ' sem'
                measure_df = group_measures_by_coverage[group][[cov_avg, cov_sem, m_avg, m_sem]].T
                df_path = path + '/' + mode + 'Average_' + measure + '.csv'
                measure_df.to_csv(path_or_buf=df_path)
                group_dict[measure] = measure_df
            df_group_dict[group] = group_dict
        if defaults.save_all_group_csvs:
            # can only do the save_all_group_csvs if save_group_csvs is done
            combined_avg_dfs = {}
            for measure in defaults.coverage_averaged_measures:
                m_list = []
                for group in df_group_dict:
                    # add group column to the df
                    group_m_df = df_group_dict[group][measure]
                    group_m_df.insert(0, "Group", group)
                    m_list.append(group_m_df)
                # combine them into one df
                combined_avg_dfs[measure] = pd.concat(m_list)
            path = user_inputs.result_path + '/Groups/CombinedGroups/AverageMeasures'
            os.makedirs(path, exist_ok=True)
            for df_key in combined_avg_dfs:
                df_path = path + '/CombinedGroups_' + mode + 'Average_' + df_key + '.csv'
                # save csv for combined group
                combined_avg_dfs[df_key].to_csv(path_or_buf=df_path)  # , index=False)
    return group_measures_by_coverage


def n_bins_average_pcov(exploded_df: pd.DataFrame) -> pd.DataFrame:
    row_avg_lists = []
    n_avgs = int(exploded_df['bin'].iloc[-1])
    for i in range(n_avgs):
        range_df = exploded_df[exploded_df['bin'] == i]
        new_columns = [[col + ' mean', col + ' sem'] for col in exploded_df.columns]
        new_columns = [item for sublist in new_columns for item in sublist]
        row_avg = pd.DataFrame([np.ones(shape=(len(new_columns),))*np.nan],
                               columns=new_columns)
        for col in range_df:
            if col != 'bin':
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    row_avg[col+' mean'] = np.nanmean(range_df[col].astype('float'))
                    try:
                        std = np.nanstd(range_df[col])
                    except ZeroDivisionError:
                        std = np.nan
                    count = np.count_nonzero(~np.isnan(range_df[col].astype('float')))
                    try:
                        row_avg[col + ' sem'] = std/np.sqrt(count)
                    except ZeroDivisionError:
                        row_avg[col + ' sem'] = np.nan
        row_avg_lists.append(row_avg)
    average_df = pd.concat(row_avg_lists)
    average_df = average_df.drop(['bin mean', 'bin sem'], axis=1)
    return average_df


def make_measures_by_pcov(group_individual_measures_dfs: dict[str, pd.DataFrame], defaults: Defaults) -> pd.DataFrame:
    # create a list (rounded to 5 digits) of all the possible coverage values
    possible_pcov_values = np.round(np.linspace(0, 1, 1001), 5)
    # now we want to sort measure values into lists at each matching coverage value
    sorted_df = sort_by_cov_measure(possible_pcov_values, group_individual_measures_dfs,
                                    defaults.coverage_averaged_measures, 'percent_coverage')
    n_rows = sorted_df.shape[0]
    # give the sorted_df a number for its group of pcov values
    sorted_df['bin'] = np.repeat(np.arange(n_rows/defaults.n_bins_percent_coverage),
                                 defaults.n_bins_percent_coverage)[:n_rows]
    # then we group every n bins and average all points in those bins
    response_columns = [item for item in sorted_df.columns if item != 'percent_coverage' and item != 'bin']
    exploded_df = sorted_df.explode(response_columns)
    # now take values of exploded_df within a bin group
    # and actually average the n points
    coverage_averages = n_bins_average_pcov(exploded_df)
    return coverage_averages


def percent_coverage_average(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], defaults: Defaults,
                             user_inputs: UserInput) -> dict[str, pd.DataFrame]:
    group_measures_by_pcov = {}
    for group in individual_measures_dfs:
        print(f'Averaging Tracks From Group {group} by percent coverage')
        group_measures_by_pcov[group] = make_measures_by_pcov(individual_measures_dfs[group], defaults)
    # have a dict of group name -> df with all measures
    if defaults.save_group_csvs:
        df_group_dict = {}
        cov_avg = 'percent_coverage mean'
        cov_sem = 'percent_coverage sem'
        for group in group_measures_by_pcov:
            group_dict = {}
            path = user_inputs.result_path + '/Groups/' + user_inputs.groups_to_paths[group] + '/AverageMeasures'
            os.makedirs(path, exist_ok=True)
            for measure in defaults.coverage_averaged_measures:
                m_avg = measure + ' mean'
                m_sem = measure + ' sem'
                measure_df = group_measures_by_pcov[group][[cov_avg, cov_sem, m_avg, m_sem]].T
                df_path = path + '/percent_coverageAverage_' + measure + '.csv'
                measure_df.to_csv(path_or_buf=df_path)
                group_dict[measure] = measure_df
            df_group_dict[group] = group_dict
        if defaults.save_all_group_csvs:
            # can only do the save_all_group_csvs if save_group_csvs is done
            combined_avg_dfs = {}
            for measure in defaults.coverage_averaged_measures:
                m_list = []
                for group in df_group_dict:
                    # add group column to the df
                    group_m_df = df_group_dict[group][measure]
                    group_m_df.insert(0, "Group", group)
                    m_list.append(group_m_df)
                    # combine them into one df
                    combined_avg_dfs[measure] = pd.concat(m_list)
                path = user_inputs.result_path + '/Groups/CombinedGroups/AverageMeasures'
                os.makedirs(path, exist_ok=True)
                for df_key in combined_avg_dfs:
                    df_path = path + '/CombinedGroups_percent_coverageAverage_' + df_key + '.csv'
                    # save csv for combined group
                    combined_avg_dfs[df_key].to_csv(path_or_buf=df_path)
    return group_measures_by_pcov
