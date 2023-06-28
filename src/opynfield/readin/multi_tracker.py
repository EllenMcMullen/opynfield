import numpy as np
import math
import pandas as pd
from scipy import interpolate
import warnings


def running_line(y_array: np.ndarray, n: int, dn: int) -> np.ndarray:
    # based on the MATLAB runline function
    # y is the input coordinate
    # n is the length of the running window in samples
    # dn is the step size of the window in samples

    num_points = len(y_array)  # number of points in the y_array
    y_line = np.zeros(shape=num_points)  # initialized results
    norm = np.zeros(shape=num_points)  # ??
    num_windows = math.ceil((num_points-n)/dn) + 1  # number of windows to smooth within
    y_fit = np.zeros(shape=(num_windows, n))  # the fit for a particular window

    # define weights with tri-weight distribution
    points = np.arange(0, n, 1)
    h = n/2
    mid_point = points.mean()
    x_weight_dist = (points-mid_point)/h

    # Tukey tri-weight kernel
    y_weights = (1 - (abs(x_weight_dist) ** 3)) ** 3

    # for each window
    for window in range(num_windows):
        y_segment = y_array[window:window + 5]  # take the segment of the data from that window
        y1 = y_segment.mean()
        y2 = (np.arange(1, n + 1) * y_segment).mean() * 2 / (n + 1)
        m_model = (y2 - y1) * 6 / (n - 1)
        b_model = y1 - m_model * (n + 1) / 2
        y_fit[window, :] = (np.arange(1, n+1) * m_model) + b_model
        y_line[window:window+n] = y_line[window:window+n] + (y_fit[window, :] * y_weights)
        norm[window:window+n] = norm[window:window+n] + y_weights

    # for the remaining points that didn't fit in a full window
    mask = np.nonzero(norm > 0)
    y_line[mask] = y_line[mask]/norm[mask]
    index = (num_windows-1)*dn+(n-1)
    num_end_pts = len(y_array) - index+1
    # noinspection PyUnboundLocalVariable
    y_line[np.arange(index-1, num_points)] = np.arange(n+1, n+num_end_pts+1) * m_model + b_model

    return y_line


def subsample(coord, sample_freq: int, sample_interval: int) -> np.ndarray:
    # sample freq is in Hz (samples per second)
    # sample_interval is time (number of seconds you want between points)
    num_pts_per_int = int(sample_interval / (1/sample_freq))
    # how many points at given sampling frequency are between points at desired sampling interval
    coord_subsample = coord[0::num_pts_per_int].copy()
    # the subsampled coordinate
    return coord_subsample


def fill_missing_data(coord: np.ndarray, time: np.ndarray) -> np.ndarray:
    # takes in either the x or y coordinate and time
    # interpolates missing values where the fly was not tracked
    time_orig = time
    # delete x where y is nan
    time = time[~np.isnan(coord)]
    # delete x where x is nan
    time = time[~np.isnan(time)]
    # delete y where y is nan
    coord = coord[~np.isnan(coord)]
    # fill in interpolated values
    f = interpolate.interp1d(time, coord, fill_value='extrapolate')
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        # catch warnings bc if x had nan y could not be calculated
        coord_new = f(time_orig)
    coord_new = pd.Series(coord_new)
    return coord_new.values


def calc_center(combined_x: np.ndarray, combined_y: np.ndarray, verbose: bool, trim: int = 0) -> tuple[float, float]:
    # this is a rough calculation of the center point
    # would be better to calculate a minimum enclosing circle and compare rough to precise calc
    x_cen_rough = np.nanmin(combined_x[trim:]) + ((np.nanmax(combined_x[trim:]) - np.nanmin(combined_x[trim:])) / 2)
    y_cen_rough = np.nanmin(combined_y[trim:]) + ((np.nanmax(combined_y[trim:]) - np.nanmin(combined_y[trim:])) / 2)
    if verbose:
        print('Combined Coordinate Center Point Calculated')
    return x_cen_rough, y_cen_rough
