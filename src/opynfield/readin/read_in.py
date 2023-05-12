from dataclasses import dataclass, field
import numpy as np
from src.opynfield.readin import multi_tracker
from src.opynfield.readin import buridian_tracker
from src.opynfield.readin import etho_excel_v1


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
        self.x = self.x - center_points_by_area[self.options][0]  # x coordinate of the arena's center point
        self.y = self.y - center_points_by_area[self.options][1]  # x coordinate of the arena's center point
        if verbose:
            print('Etho V1 Track Centered')


def read_track_types(file_type: str, groups_with_file_type: list[str], verbose: bool, arena_radius_cm: float,
                     running_window_length: int, window_step_size: int, sample_freq: int, time_bin_size: int,
                     all_tracks: list[Track]) -> list[Track]:
    if file_type == 'Buridian Tracker':
        all_tracks = buridian_tracker.read_buridian(groups_with_file_type, verbose, arena_radius_cm,
                                                    running_window_length, window_step_size, sample_freq,
                                                    time_bin_size, all_tracks)
    if file_type == 'Ethovision Excel Version 1':
        all_tracks = etho_excel_v1.read_ethov1(groups_with_file_type, verbose, sample_freq, time_bin_size, all_tracks)

    return all_tracks
