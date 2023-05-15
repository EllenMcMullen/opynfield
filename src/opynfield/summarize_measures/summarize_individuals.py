from collections import defaultdict
from src.opynfield.calculate_measures.standard_track import StandardTrack
from src.opynfield.config.defaults_settings import Defaults


def individual_measures_to_dfs(tracks_by_groups: defaultdict[str: list[StandardTrack]], defaults: Defaults):
    for group in tracks_by_groups:
        for i, track in enumerate(tracks_by_groups[group]):
            print(f'Summarizing Track {i}')
            # save the measures into an appropriate df for the group
            # also save one for the

    return
