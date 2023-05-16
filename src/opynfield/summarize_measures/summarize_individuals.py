import os
from collections import defaultdict
from src.opynfield.calculate_measures.standard_track import StandardTrack
from src.opynfield.config.defaults_settings import Defaults
from src.opynfield.config.user_input import UserInput


def individual_measures_to_dfs(tracks_by_groups: defaultdict[str, list[StandardTrack]], defaults: Defaults,
                               user_inputs: UserInput):
    group_dfs = {}
    for group in tracks_by_groups:
        print(f'Summarizing Tracks From Group {group}')
        # get a dict of df for each attribute we care about
        # save that dict to a dict by group name
        group_dfs[group] = StandardTrack.to_dataframes(tracks_by_groups[group], ['pica_asymptote', 'pgca_asymptote'])
        if defaults.save_group_csvs:
            # make a dir for results -> individuals -> group -> measures
            path = user_inputs.result_path + '/Individuals/' + user_inputs.groups_to_paths[group] + '/Measures'
            os.makedirs(path, exist_ok=True)
            for df_key in group_dfs[group]:
                df_path = path + '/' + df_key + '.csv'
                group_dfs[group][df_key].to_csv(path_or_buf=df_path)
                # save csv for the group
    return group_dfs
