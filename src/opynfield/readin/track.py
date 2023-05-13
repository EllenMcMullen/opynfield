from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.opynfield.readin import multi_tracker


@dataclass
class Track:
    # dataclass for standardized track after data is read in and wrangled
    group: str  # can change to enum
    x: np.ndarray = field(repr=False)  # x coordinate
    y: np.ndarray = field(repr=False)  # y coordinate
    t: np.ndarray = field(repr=False)  # time
    track_type: str  # which data type this came from -> can change to enum
    options: list
    # for buri: x and y center coordinates (in cm) then arena_radius_px
    # for ethov1: arena number
    # for ethov2: arena number
    standardized: bool  # has the track been completely standardized yet

    def buri_convert_units(self, arena_radius_cm: float, arena_radius_px: int, verbose: bool):
        assert self.track_type == 'Buridian Tracker'
        self.x = self.x * (arena_radius_cm / arena_radius_px)  # convert x coordinate from pixels to cm
        self.y = self.y * (arena_radius_cm / arena_radius_px)  # convert y coordinate from pixels to cm
        self.t = self.t / 1000  # convert time from ms to s
        if verbose:
            print('Buri Units Converted')

    def buri_convert_to_center(self, center_point_x: float, center_point_y: float, verbose: bool):
        assert self.track_type == 'Buridian Tracker'
        # subtract the center point so that the track coordinate system will be centered at (0,0)
        self.x = self.x - center_point_x
        self.y = self.y - center_point_y
        if verbose:
            print('Buri Units Centered')

    def buri_running_line(self, running_window_length: int, window_step_size: int, verbose: bool):
        assert self.track_type == 'Buridian Tracker'
        # smooth the coordinates using the same function used in ethovision tracks
        self.x = multi_tracker.running_line(self.x, running_window_length, window_step_size)
        self.y = multi_tracker.running_line(self.y, running_window_length, window_step_size)
        if verbose:
            print('Buri Track Smoothed')

    def buri_subsample(self, sample_freq: int, time_bin_size: int, verbose: bool):
        assert self.track_type == 'Buridian Tracker'
        # subsample the coordinates to the desired sampling frequency
        self.x = multi_tracker.subsample(self.x, sample_freq, time_bin_size)
        self.y = multi_tracker.subsample(self.y, sample_freq, time_bin_size)
        self.t = multi_tracker.subsample(self.t, sample_freq, time_bin_size)
        if verbose:
            print('Buri Track Subsampled')

    def buri_fill_missing(self, verbose: bool):
        assert self.track_type == 'Buridian Tracker'
        # fill missing data using linear extrapolation
        self.x = multi_tracker.fill_missing_data(self.x, self.t)
        self.y = multi_tracker.fill_missing_data(self.y, self.t)
        if verbose:
            print('Buri Track Missing Values Filled')

    def etho_v1_numeric(self, verbose: bool):
        assert self.track_type == 'Ethovision Excel Version 1'
        # in v1 the values are stored as floats but there are string '-' for missing values that we set to nan
        for i in range(len(self.x)):
            if type(self.x[i]) != float:
                self.x[i] = np.nan
            if type(self.y[i]) != float:
                self.y[i] = np.nan
        self.x = self.x.astype(np.float64)
        self.y = self.y.astype(np.float64)
        self.t = self.t.astype(np.float64)
        if verbose:
            print('Etho V1 Track Converted To Numeric')

    def etho_v1_subsample(self, sample_freq: int, time_bin_size: int, verbose: bool):
        assert self.track_type == 'Ethovision Excel Version 1'
        self.x = multi_tracker.subsample(self.x, sample_freq, time_bin_size)
        self.y = multi_tracker.subsample(self.y, sample_freq, time_bin_size)
        self.t = multi_tracker.subsample(self.t, sample_freq, time_bin_size)
        if verbose:
            print('Etho V1 Track Subsampled')

    def etho_v1_fill_missing(self, verbose: bool):
        assert self.track_type == 'Ethovision Excel Version 1'
        self.x = multi_tracker.fill_missing_data(self.x, self.t)
        self.y = multi_tracker.fill_missing_data(self.y, self.t)
        if verbose:
            print('Etho V1 Track Missing Values Filled')

    def etho_v1_convert_to_center(self, center_points_by_area: dict[str: tuple[float, float]], verbose: bool):
        assert self.track_type == 'Ethovision Excel Version 1'
        self.x = self.x - center_points_by_area[self.options[0]][0]  # x coordinate of the arena's center point
        self.y = self.y - center_points_by_area[self.options[0]][1]  # x coordinate of the arena's center point
        if verbose:
            print('Etho V1 Track Centered')

    def etho_v2_numeric(self, verbose):
        # in v1 the values are stored as number strings, so we try to convert to float
        # but there are string '-' for missing values that won't convert to float that we set to nan
        for i in range(len(self.x)):
            try:
                self.x[i] = float(self.x[i])
            except ValueError:
                self.x[i] = np.nan
            try:
                self.y[i] = float(self.y[i])
            except ValueError:
                self.y[i] = np.nan
        self.x = self.x.astype(np.float64)
        self.y = self.y.astype(np.float64)
        self.t = self.t.astype(np.float64)
        if verbose:
            print('Etho V2 Track Converted To Numeric')

    def etho_v2_subsample(self, sample_freq: int, time_bin_size: int, verbose: bool):
        assert self.track_type == 'Ethovision Excel Version 2'
        self.x = multi_tracker.subsample(self.x, sample_freq, time_bin_size)
        self.y = multi_tracker.subsample(self.y, sample_freq, time_bin_size)
        self.t = multi_tracker.subsample(self.t, sample_freq, time_bin_size)
        if verbose:
            print('Etho V2 Track Subsampled')

    def etho_v2_fill_missing(self, verbose: bool):
        assert self.track_type == 'Ethovision Excel Version 2'
        self.x = multi_tracker.fill_missing_data(self.x, self.t)
        self.y = multi_tracker.fill_missing_data(self.y, self.t)
        if verbose:
            print('Etho V2 Track Missing Values Filled')

    def etho_v2_convert_to_center(self, center_points_by_area: dict[str: tuple[float, float]], verbose: bool):
        assert self.track_type == 'Ethovision Excel Version 2'
        self.x = self.x - center_points_by_area[self.options][0]  # x coordinate of the arena's center point
        self.y = self.y - center_points_by_area[self.options][1]  # x coordinate of the arena's center point
        if verbose:
            print('Etho V2 Track Centered')

    def etho_txt_numeric(self, verbose: bool):
        self.x = pd.to_numeric(self.x, errors='coerce')
        self.y = pd.to_numeric(self.y, errors='coerce')
        self.t = pd.to_numeric(self.t, errors='coerce')
        if verbose:
            print('Etho Text Track Converted To Numeric')

    def etho_txt_subsample(self, sample_freq: int, time_bin_size: int, verbose: bool):
        assert self.track_type == 'Ethovision Text'
        self.x = multi_tracker.subsample(self.x, sample_freq, time_bin_size)
        self.y = multi_tracker.subsample(self.y, sample_freq, time_bin_size)
        self.t = multi_tracker.subsample(self.t, sample_freq, time_bin_size)
        if verbose:
            print('Etho Text Track Subsampled')

    def etho_txt_fill_missing(self, verbose: bool):
        assert self.track_type == 'Ethovision Text'
        self.x = multi_tracker.fill_missing_data(self.x, self.t)
        self.y = multi_tracker.fill_missing_data(self.y, self.t)
        if verbose:
            print('Etho Text Track Missing Values Filled')

    def etho_txt_convert_to_center(self, center_points_by_area: dict[str: tuple[float, float]], verbose: bool):
        assert self.track_type == 'Ethovision Text'
        self.x = self.x - center_points_by_area[self.options][0]  # x coordinate of the arena's center point
        self.y = self.y - center_points_by_area[self.options][1]  # x coordinate of the arena's center point
        if verbose:
            print('Etho Text Track Centered')

    def etho_ml_numeric(self, verbose: bool):
        assert self.track_type == 'Ethovision Through MATLAB'
        for i in range(len(self.x)):
            if type(self.x[i]) != np.float64:
                self.x[i] = np.nan
            if type(self.y[i]) != np.float64:
                self.y[i] = np.nan
        self.x = self.x.astype(np.float64)
        self.y = self.y.astype(np.float64)
        self.t = self.t.astype(np.float64)
        if verbose:
            print('Etho ML Track Converted To Numeric')

    def etho_ml_subsample(self, sample_freq: int, time_bin_size: int, verbose: bool):
        assert self.track_type == 'Ethovision Through MATLAB'
        self.x = multi_tracker.subsample(self.x, sample_freq, time_bin_size)
        self.y = multi_tracker.subsample(self.y, sample_freq, time_bin_size)
        self.t = multi_tracker.subsample(self.t, sample_freq, time_bin_size)
        if verbose:
            print('Etho ML Track Subsampled')

    def etho_ml_fill_missing(self, verbose: bool):
        assert self.track_type == 'Ethovision Through MATLAB'
        self.x = multi_tracker.fill_missing_data(self.x, self.t)
        self.y = multi_tracker.fill_missing_data(self.y, self.t)
        if verbose:
            print('Etho ML Track Missing Values Filled')

    def etho_ml_convert_to_center(self, track_center: tuple[float, float], verbose: bool):
        assert self.track_type == 'Ethovision Through MATLAB'
        self.x = self.x - track_center[0]  # x coordinate of the track's center point
        self.y = self.y - track_center[1]  # x coordinate of the track's center point
        if verbose:
            print('Etho ML Track Centered')

    def anymaze_center_numeric(self, verbose: bool):
        assert self.track_type == 'AnyMaze Center'
        self.x = pd.to_numeric(self.x, errors='coerce')
        self.y = pd.to_numeric(self.y, errors='coerce')
        if verbose:
            print('Anymaze Center Point Track Converted To Numeric')

    def anymaze_center_running_line(self, running_window_length: int, window_step_size: int, verbose: bool):
        assert self.track_type == 'AnyMaze Center'
        # smooth the coordinates using the same function used in ethovision tracks
        self.x = multi_tracker.running_line(self.x, running_window_length, window_step_size)
        self.y = multi_tracker.running_line(self.y, running_window_length, window_step_size)
        if verbose:
            print('AnyMaze Center Point Track Smoothed')

    def anymaze_center_subsample(self, sample_freq: int, time_bin_size: int, verbose: bool):
        assert self.track_type == 'AnyMaze Center'
        # subsample the coordinates to the desired sampling frequency
        self.x = multi_tracker.subsample(self.x, sample_freq, time_bin_size)
        self.y = multi_tracker.subsample(self.y, sample_freq, time_bin_size)
        self.t = multi_tracker.subsample(self.t, sample_freq, time_bin_size)
        if verbose:
            print('AnyMaze Center Point Track Subsampled')

    def anymaze_center_fill_missing(self, verbose: bool):
        assert self.track_type == 'AnyMaze Center'
        # fill missing data using linear extrapolation
        self.x = multi_tracker.fill_missing_data(self.x, self.t)
        self.y = multi_tracker.fill_missing_data(self.y, self.t)
        if verbose:
            print('AnyMaze Center Point Track Missing Values Filled')

    def anymaze_center_convert_to_center(self, track_center, verbose):
        assert self.track_type == 'AnyMaze Center'
        # these are all in pixels
        self.x = self.x - track_center[0]
        self.y = self.y - track_center[1]
        if verbose:
            print('AnyMaze Center Point Units Centered')

    def anymaze_center_convert_units(self, arena_radius_cm, trim):
        assert self.track_type == 'AnyMaze Center'
        # find the radius in pixels
        arena_radius_px_x = (np.nanmax(self.x[trim:]) - np.nanmin(self.x[trim:])) / 2
        arena_radius_px_y = (np.nanmax(self.y[trim:]) - np.nanmin(self.y[trim:])) / 2
        arena_radius_px = max(arena_radius_px_x, arena_radius_px_y)
        # convert units from pixels to cm
        self.x = self.x * (arena_radius_cm / arena_radius_px)
        self.y = self.y * (arena_radius_cm / arena_radius_px)

    def anymaze_head_numeric(self, verbose: bool):
        assert self.track_type == 'AnyMaze Head'
        self.x = pd.to_numeric(self.x, errors='coerce')
        self.y = pd.to_numeric(self.y, errors='coerce')
        if verbose:
            print('Anymaze Center Point Track Converted To Numeric')

    def anymaze_head_running_line(self, running_window_length: int, window_step_size: int, verbose: bool):
        assert self.track_type == 'AnyMaze Head'
        # smooth the coordinates using the same function used in ethovision tracks
        self.x = multi_tracker.running_line(self.x, running_window_length, window_step_size)
        self.y = multi_tracker.running_line(self.y, running_window_length, window_step_size)
        if verbose:
            print('AnyMaze Center Point Track Smoothed')

    def anymaze_head_subsample(self, sample_freq: int, time_bin_size: int, verbose: bool):
        assert self.track_type == 'AnyMaze Head'
        # subsample the coordinates to the desired sampling frequency
        self.x = multi_tracker.subsample(self.x, sample_freq, time_bin_size)
        self.y = multi_tracker.subsample(self.y, sample_freq, time_bin_size)
        self.t = multi_tracker.subsample(self.t, sample_freq, time_bin_size)
        if verbose:
            print('AnyMaze Center Point Track Subsampled')

    def anymaze_head_fill_missing(self, verbose: bool):
        assert self.track_type == 'AnyMaze Head'
        # fill missing data using linear extrapolation
        self.x = multi_tracker.fill_missing_data(self.x, self.t)
        self.y = multi_tracker.fill_missing_data(self.y, self.t)
        if verbose:
            print('AnyMaze Center Point Track Missing Values Filled')

    def anymaze_head_convert_to_center(self, track_center, verbose):
        assert self.track_type == 'AnyMaze Head'
        # these are all in pixels
        self.x = self.x - track_center[0]
        self.y = self.y - track_center[1]
        if verbose:
            print('AnyMaze Center Point Units Centered')

    def anymaze_head_convert_units(self, arena_radius_cm, trim):
        assert self.track_type == 'AnyMaze Head'
        # find the radius in pixels
        arena_radius_px_x = (np.nanmax(self.x[trim:]) - np.nanmin(self.x[trim:])) / 2
        arena_radius_px_y = (np.nanmax(self.y[trim:]) - np.nanmin(self.y[trim:])) / 2
        arena_radius_px = max(arena_radius_px_x, arena_radius_px_y)
        # convert units from pixels to cm
        self.x = self.x * (arena_radius_cm / arena_radius_px)
        self.y = self.y * (arena_radius_cm / arena_radius_px)
