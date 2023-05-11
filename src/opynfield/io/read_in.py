from dataclasses import dataclass, field
import numpy as np
from src.opynfield.io.multi_tracker import running_line
from src.opynfield.io.multi_tracker import subsample
from src.opynfield.io.multi_tracker import fill_missing_data


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
    standardized: bool  # has the track been completely standardized yet

    def buri_convert_units(self, arena_radius_cm: float, arena_radius_px: int, verbose: bool):
        self.x = self.x * (arena_radius_cm / arena_radius_px)  # convert x coordinate from pixels to cm
        self.y = self.y * (arena_radius_cm / arena_radius_px)  # convert y coordinate from pixels to cm
        self.t = self.t / 1000  # convert time from ms to s
        if verbose:
            print('Buri Units Converted')
        return

    def buri_convert_to_center(self, center_point_x: float, center_point_y: float, verbose: bool):
        # subtract the center point so that the track coordinate system will be centered at (0,0)
        self.x = self.x - center_point_x
        self.y = self.y - center_point_y
        if verbose:
            print('Buri Units Centered')
        return

    def buri_running_line(self, running_window_length: int, window_step_size: int, verbose: bool):
        # smooth the coordinates using the same function used in ethovision tracks
        self.x = running_line(self.x, running_window_length, window_step_size)
        self.y = running_line(self.y, running_window_length, window_step_size)
        if verbose:
            print('Buri Track Smoothed')
        return

    def buri_subsample(self, sample_freq: int, time_bin_size: int, verbose: bool):
        # subsample the coordinates to the desired sampling frequency
        self.x = subsample(self.x, sample_freq, time_bin_size)
        self.y = subsample(self.y, sample_freq, time_bin_size)
        self.t = subsample(self.t, sample_freq, time_bin_size)
        if verbose:
            print('Buri Track Subsampled')

    def buri_fill_missing(self, verbose: bool):
        # fill missing data using linear extrapolation
        self.x = fill_missing_data(self.x, self.t)
        self.y = fill_missing_data(self.y, self.t)
        if verbose:
            print('Buri Track Missing Values Filled')
