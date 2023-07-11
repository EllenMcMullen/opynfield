import opynfield.readin.track
from opynfield.readin import read_in
import numpy as np


def run_all_track_types(
    groups_and_types: dict[str, list[str]],
    verbose: bool,
    arena_radius_cm: float,
    running_window_length: int,
    window_step_size: int,
    sample_freq: int,
    time_bin_size: int,
    trim: int,
) -> list[opynfield.readin.track.Track]:
    """This function coordinates the entire read-in process

    :param groups_and_types: the input information of which groups were recorded with which filetypes
    :type groups_and_types: dict[str, list[str]]
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :param arena_radius_cm: the radius of the arena in which the track was recorded, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type arena_radius_cm: float
    :param running_window_length: a smoothing function parameter set to match ethovision, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type running_window_length: int
    :param window_step_size: a smoothing function parameter set to match ethovision, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type window_step_size: int
    :param sample_freq: the frame rate that the track was recorded with, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type sample_freq: int
    :param time_bin_size: how many seconds should be aggregated together, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type time_bin_size: int
    :param trim: how many points are recorded before the animal enters the arena (maximum of all animals in this track type), sourced from :class:`opynfield.config.user_input.UserInput` object
    :type trim: int
    :return: all the Tracks that were read in
    :rtype: list[opynfield.readin.track.Track]
    """
    file_types_included = groups_to_types(groups_and_types)  # what file types to run
    print(file_types_included)
    groups_by_filetype = types_to_groups(file_types_included, groups_and_types)
    print(groups_by_filetype)
    all_tracks = list()
    for f in file_types_included:
        print(f"Read In {f} Files For Groups {groups_by_filetype[f]}")
        all_tracks = read_in.read_track_types(
            f,
            groups_by_filetype[f],
            verbose,
            arena_radius_cm,
            running_window_length,
            window_step_size,
            sample_freq,
            time_bin_size,
            trim,
            all_tracks,
        )
    return all_tracks


def groups_to_types(groups_and_types: dict[str, list[str]]) -> list[str]:
    """This function makes a list of which file types are used in the run

    :param groups_and_types: the input information of which groups were recorded with which filetypes
    :type groups_and_types: dict[str, list[str]]
    :return: the filetypes included in the run
    :rtype: list[str]
    """
    # make lists of filetypes in this run
    file_types_included = list()
    for group in groups_and_types:
        for f_type in groups_and_types[group]:
            file_types_included.append(f_type)
    file_types_included = list(np.unique(np.array(file_types_included)))
    return file_types_included


def types_to_groups(
    file_types_included: list[str], groups_and_types: dict[str, list[str]]
) -> dict[str, list[str]]:
    """This function creates a list for each filetype of which groups were recorded in that filetype

    :param file_types_included: which filetypes were included in the run
    :type file_types_included: list[str]
    :param groups_and_types: the input information of which groups were recorded with which filetypes
    :type groups_and_types: dict[str, list[str]]
    :return: which groups were recorded in which filetypes
    :rtype: dict[str, list[str]]
    """
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
