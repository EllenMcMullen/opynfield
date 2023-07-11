from opynfield.readin import buridian_tracker
from opynfield.readin import etho_tracker
from opynfield.readin import anymaze_tracker

from opynfield.readin.track import Track


def read_track_types(
    file_type: str,
    groups_with_file_type: list[str],
    verbose: bool,
    arena_radius_cm: float,
    running_window_length: int,
    window_step_size: int,
    sample_freq: int,
    time_bin_size: int,
    trim,
    all_tracks: list[Track],
) -> list[Track]:
    """This function coordinates reading in all the data from each track type

    :param file_type: the file type to read in
    :type file_type: str
    :param groups_with_file_type: which groups have tracks recorded in that file type
    :type groups_with_file_type: list[str]
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :param arena_radius_cm: the radius of the arena in which the track was recorded (only required for buridian and anymaze trackers), sourced from :class:`opynfield.config.user_input.UserInput` object
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
    :param all_tracks: a list with all the Track objects from previously read-in datatypes
    :type all_tracks: list[Track]
    :return: a list of Track objects with a consistent format for x y and t tracking points
    :rtype: list[Track]
    """
    if file_type == "Buridian Tracker":
        all_tracks = buridian_tracker.read_buridian(
            groups_with_file_type,
            verbose,
            arena_radius_cm,
            running_window_length,
            window_step_size,
            sample_freq,
            time_bin_size,
            all_tracks,
        )
    if file_type == "Ethovision Excel Version 1":
        all_tracks = etho_tracker.read_etho_v1(
            groups_with_file_type, verbose, sample_freq, time_bin_size, all_tracks
        )
    if file_type == "Ethovision Excel Version 2":
        all_tracks = etho_tracker.read_etho_v2(
            groups_with_file_type, verbose, sample_freq, time_bin_size, all_tracks
        )
    if file_type == "Ethovision Text":
        all_tracks = etho_tracker.read_etho_txt(
            groups_with_file_type, verbose, sample_freq, time_bin_size, all_tracks
        )
    if file_type == "Ethovision Through MATLAB":
        all_tracks = etho_tracker.read_etho_ml(
            groups_with_file_type, verbose, sample_freq, time_bin_size, all_tracks
        )
    if file_type == "AnyMaze Center":
        all_tracks = anymaze_tracker.read_anymaze_center(
            groups_with_file_type,
            verbose,
            arena_radius_cm,
            running_window_length,
            window_step_size,
            sample_freq,
            time_bin_size,
            trim,
            all_tracks,
        )
    if file_type == "AnyMaze Head":
        all_tracks = anymaze_tracker.read_anymaze_head(
            groups_with_file_type,
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
