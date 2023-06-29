from opynfield.readin.track import Track
from tkinter import filedialog
import pandas as pd
import numpy as np
import datetime
from opynfield.readin import multi_tracker


def read_anymaze_center(groups_with_file_type: list[str], verbose: bool, arena_radius_cm: float,
                        running_window_length: int, window_step_size: int, sample_freq: int, time_bin_size: int,
                        trim, all_tracks: list[Track]) -> list[Track]:
    for anymaze_group in groups_with_file_type:
        if verbose:
            print(f'Running Anymaze Center Point Tracker Files For Group: {anymaze_group}')
        title = f"Select .csv files for {anymaze_group}"
        # select .csv buri files for the groups
        data_files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")], title=title)
        for file_num in range(len(data_files)):
            if verbose:
                print(f"{anymaze_group}, File{file_num + 1} Out Of {len(data_files)}")
            # read in each file's data
            file_data = pd.read_csv(data_files[file_num], sep=',', lineterminator='\n')
            file_data = file_data[:-1]
            track = Track(anymaze_group, file_data['Centre position X'].to_numpy(),
                          file_data['Centre position Y'].to_numpy(), file_data['Time'].to_numpy(),
                          'AnyMaze Center', [], False)
            # put track coordinates through standardization procedures
            track.anymaze_center_numeric(verbose)
            track.t = convert_time_stamp(track.t, verbose)
            track.anymaze_center_running_line(running_window_length, window_step_size, verbose)
            track.anymaze_center_subsample(sample_freq, time_bin_size, verbose)
            track.anymaze_center_fill_missing(verbose)
            track_center = multi_tracker.calc_center(track.x, track.y, verbose, trim)
            track.anymaze_center_convert_to_center(track_center, verbose)
            track.anymaze_center_convert_units(arena_radius_cm, trim)
            all_tracks.append(track)
    return all_tracks


def read_anymaze_head(groups_with_file_type: list[str], verbose: bool, arena_radius_cm: float,
                      running_window_length: int, window_step_size: int, sample_freq: int, time_bin_size: int,
                      trim, all_tracks: list[Track]) -> list[Track]:
    for anymaze_group in groups_with_file_type:
        if verbose:
            print(f'Running Anymaze Head Point Tracker Files For Group: {anymaze_group}')
        title = f"Select .csv files for {anymaze_group}"
        # select .csv buri files for the groups
        data_files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")], title=title)
        for file_num in range(len(data_files)):
            if verbose:
                print(f"{anymaze_group}, File{file_num + 1} Out Of {len(data_files)}")
            # read in each file's data
            file_data = pd.read_csv(data_files[file_num], sep=',', lineterminator='\n')
            file_data = file_data[:-1]
            track = Track(anymaze_group, file_data['Head position X'].to_numpy(),
                          file_data['Head position Y'].to_numpy(), file_data['Time'].to_numpy(),
                          'AnyMaze Head', [], False)
            # put track coordinates through standardization procedures
            track.anymaze_head_numeric(verbose)
            track.t = convert_time_stamp(track.t, verbose)
            track.anymaze_head_running_line(running_window_length, window_step_size, verbose)
            track.anymaze_head_subsample(sample_freq, time_bin_size, verbose)
            track.anymaze_head_fill_missing(verbose)
            track_center = multi_tracker.calc_center(track.x, track.y, verbose, trim)
            track.anymaze_head_convert_to_center(track_center, verbose)
            track.anymaze_head_convert_units(arena_radius_cm, trim)
            all_tracks.append(track)
    return all_tracks


def convert_time_stamp(time_stamp, verbose):
    time_elapsed = np.zeros(len(time_stamp))  # initialize results
    d = datetime.date(2018, 11, 9)  # dummy date
    t_init = datetime.time.fromisoformat('0'+time_stamp[0])
    if verbose:
        print(f'Initial Time: {t_init}')
    t_dt_init = datetime.datetime.combine(d, t_init)  # time at start
    for i in range(len(time_stamp)):
        t_string = '0' + time_stamp[i]
        t_time = datetime.time.fromisoformat(t_string)
        t_datetime = datetime.datetime.combine(d, t_time)  # time at point
        t_delta = t_datetime - t_dt_init
        time_elapsed[i] = t_delta.total_seconds()  # time since start in seconds
    return time_elapsed
