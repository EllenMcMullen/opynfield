import os
from collections import defaultdict
import pandas as pd
from opynfield.calculate_measures.standard_track import StandardTrack
from opynfield.config.defaults_settings import Defaults
from opynfield.config.user_input import UserInput


def individual_measures_to_dfs(tracks_by_groups: defaultdict[str, list[StandardTrack]], defaults: Defaults,
                               user_inputs: UserInput) -> dict[str, dict[str, pd.DataFrame]]:
    group_dfs = {}
    for group in tracks_by_groups:
        print(f'Summarizing Tracks From Group {group}')
        # get a dict of df for each attribute we care about
        # save that dict to a dict by group name
        g_df, fields = StandardTrack.to_dataframes(tracks_by_groups[group], ['pica_asymptote', 'pgca_asymptote'])
        group_dfs[group] = g_df
        if defaults.save_group_csvs:
            # make a dir for results -> individuals -> group -> measures
            path = user_inputs.result_path + '/Individuals/' + user_inputs.groups_to_paths[group] + '/Measures'
            os.makedirs(path, exist_ok=True)
            for df_key in group_dfs[group]:
                df_path = path + '/' + df_key + '.csv'
                group_dfs[group][df_key].to_csv(path_or_buf=df_path, index=False)
                # save csv for the group
    if defaults.save_all_group_csvs:
        # add group names to group dfs, then concat the dfs from each group together to make one
        combined_dfs = {}
        # for each measure
        for measure in fields:  # noqa
            # pull that measure from each group
            m_list = []
            for group in group_dfs:
                g_df = group_dfs[group][measure]
                g_df.insert(0, "Group", group)
                m_list.append(g_df)
            # combine them into one df
            combined_dfs[measure] = pd.concat(m_list)
        path = user_inputs.result_path + '/Individuals/CombinedGroups/Measures'
        os.makedirs(path, exist_ok=True)
        for df_key in combined_dfs:
            df_path = path + '/CombinedGroups_' + df_key + '.csv'
            combined_dfs[df_key].to_csv(path_or_buf=df_path, index=False)
            # save csv for the combined group
    return group_dfs
