import opynfield.readin.track
from opynfield.readin import read_in
import numpy as np


def run_all_track_types(groups_and_types: dict[str: list[str]], verbose: bool, arena_radius_cm: float,
                        running_window_length: int, window_step_size: int, sample_freq: int, time_bin_size: int,
                        trim: int) -> list[opynfield.readin.track.Track]:
    file_types_included = groups_to_types(groups_and_types)  # what file types to run
    print(file_types_included)
    groups_by_filetype = types_to_groups(file_types_included, groups_and_types)
    print(groups_by_filetype)
    all_tracks = list()
    for f in file_types_included:
        print(f"Read In {f} Files For Groups {groups_by_filetype[f]}")
        all_tracks = read_in.read_track_types(f, groups_by_filetype[f], verbose, arena_radius_cm,
                                              running_window_length, window_step_size, sample_freq, time_bin_size,
                                              trim, all_tracks)
    return all_tracks


def groups_to_types(groups_and_types: dict[str: list[str]]) -> list[str]:
    # make lists of filetypes in this run
    file_types_included = list()
    for group in groups_and_types:
        for f_type in groups_and_types[group]:
            file_types_included.append(f_type)
    file_types_included = list(np.unique(np.array(file_types_included)))
    return file_types_included


def types_to_groups(file_types_included: list[str], groups_and_types: dict[str: list[str]]) -> dict[str: list[str]]:
    # for each type in the run, make a list of groups in that type
    groups_by_filetype = dict()  # store results
    for f_type in file_types_included:
        # find all the groups that have this file type
        groups = list()  # list of groups with file type
        for gs in groups_and_types:
            # does this group include this file type
            if f_type in groups_and_types[gs]:
                groups.append(gs)  # if so add it
        groups_by_filetype[f_type] = groups
    return groups_by_filetype
