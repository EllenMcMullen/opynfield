from opynfield.readin.track import Track
from tkinter import filedialog
import pandas as pd
import numpy as np
import datetime
from opynfield.readin import multi_tracker


def read_anymaze_center(
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
    """This function reads in all the tracks from the Anymaze tracker format that recorded the center position of the
    animal subject (rather than the head position). The function extracts the x, y, and t information and smooths,
    centers, and converts the units of the track.

    :param groups_with_file_type: which groups have tracks recorded in this type
    :type groups_with_file_type: list[str]
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
    :param all_tracks: a list with all the Track objects from previously read-in datatypes
    :type all_tracks: list[Track]
    :return: a list of Track objects with a consistent format for x y and t tracking points
    :rtype: list[Track]
    """
    for anymaze_group in groups_with_file_type:
        if verbose:
            print(
                f"Running Anymaze Center Point Tracker Files For Group: {anymaze_group}"
            )
        title = f"Select .csv files for {anymaze_group}"
        # select .csv buri files for the groups
        data_files = filedialog.askopenfilenames(
            filetypes=[("CSV files", "*.csv")], title=title
        )
        for file_num in range(len(data_files)):
            if verbose:
                print(f"{anymaze_group}, File{file_num + 1} Out Of {len(data_files)}")
            # read in each file's data
            file_data = pd.read_csv(data_files[file_num], sep=",")#, lineterminator="\n")
            #file_data = file_data[:-1]
            track = Track(
                anymaze_group,
                file_data["Centre position X"].to_numpy(),
                file_data["Centre position Y"].to_numpy(),
                file_data["Time"].to_numpy(),
                "AnyMaze Center",
                [],
                False,
            )
            # put track coordinates through standardization procedures
            track.anymaze_center_numeric(verbose)
            track.t = convert_time_stamp(track.t, verbose)
            track.anymaze_center_running_line(
                running_window_length, window_step_size, verbose
            )
            track.anymaze_center_subsample(sample_freq, time_bin_size, verbose)
            track.anymaze_center_fill_missing(verbose)
            track_center = multi_tracker.calc_center(track.x, track.y, verbose, trim)
            track.anymaze_center_convert_to_center(track_center, verbose)
            track.anymaze_center_convert_units(arena_radius_cm, trim)
            track.standardized = True
            all_tracks.append(track)
    return all_tracks


def read_anymaze_head(
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
    """This function reads in all the tracks from the Anymaze tracker format that recorded the head position of the
    animal subject (rather than the body center point). The function extracts the x, y, and t information and smooths,
    centers, and converts the units of the track.

    :param groups_with_file_type: which groups have tracks recorded in this type
    :type groups_with_file_type: list[str]
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
    :param all_tracks: a list with all the Track objects from previously read-in datatypes
    :type all_tracks: list[Track]
    :return: a Track object with a consistent format for x y and t tracking points
    :rtype: list[Track]
    """
    for anymaze_group in groups_with_file_type:
        if verbose:
            print(
                f"Running Anymaze Head Point Tracker Files For Group: {anymaze_group}"
            )
        title = f"Select .csv files for {anymaze_group}"
        # select .csv buri files for the groups
        data_files = filedialog.askopenfilenames(
            filetypes=[("CSV files", "*.csv")], title=title
        )
        for file_num in range(len(data_files)):
            if verbose:
                print(f"{anymaze_group}, File{file_num + 1} Out Of {len(data_files)}")
            # read in each file's data
            file_data = pd.read_csv(data_files[file_num], sep=",")#, lineterminator="\n")
            #file_data = file_data[:-1]
            track = Track(
                anymaze_group,
                file_data["Head position X"].to_numpy(),
                file_data["Head position Y"].to_numpy(),
                file_data["Time"].to_numpy(),
                "AnyMaze Head",
                [],
                False,
            )
            # put track coordinates through standardization procedures
            track.anymaze_head_numeric(verbose)
            track.t = convert_time_stamp(track.t, verbose)
            track.anymaze_head_running_line(
                running_window_length, window_step_size, verbose
            )
            track.anymaze_head_subsample(sample_freq, time_bin_size, verbose)
            track.anymaze_head_fill_missing(verbose)
            track_center = multi_tracker.calc_center(track.x, track.y, verbose, trim)
            track.anymaze_head_convert_to_center(track_center, verbose)
            track.anymaze_head_convert_units(arena_radius_cm, trim)
            track.standardized = True
            all_tracks.append(track)
    return all_tracks


def convert_time_stamp(time_stamp, verbose):
    """This function converts the time column from the form 00:00:00.00 (or similar) to the form 0.00
    Note: there seems to be some inconsistency with how the time stamp column is saved in the Anymaze format, please
    submit an error report if you encounter a new format that is not addressed in this function.

    :param time_stamp: the original time column
    :type time_stamp: np.ndarray
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: the re-formatted time column
    :rtype: np.ndarray
    """
    time_elapsed = np.zeros(len(time_stamp))  # initialize results
    d = datetime.date(2018, 11, 9)  # dummy date
    t_init = datetime.time.fromisoformat("0" + time_stamp[0])
    if verbose:
        print(f"Initial Time: {t_init}")
    t_dt_init = datetime.datetime.combine(d, t_init)  # time at start
    for i in range(len(time_stamp)):
        t_string = "0" + time_stamp[i]
        t_time = datetime.time.fromisoformat(t_string)
        t_datetime = datetime.datetime.combine(d, t_time)  # time at point
        t_delta = t_datetime - t_dt_init
        time_elapsed[i] = t_delta.total_seconds()  # time since start in seconds
    return time_elapsed
