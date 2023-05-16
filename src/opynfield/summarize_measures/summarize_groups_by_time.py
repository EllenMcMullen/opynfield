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


def coverage_average(individual_measures_dfs: dict[str, dict[str, pd.DataFrame]], defaults: Defaults,
                     user_inputs: UserInput):
    pass
