import numpy as np
import math
import warnings
from scipy.optimize import curve_fit
from collections import defaultdict
from opynfield.readin.run_all import run_all_track_types
from opynfield.config.user_input import test_user_config
from opynfield.config.defaults_settings import test_defaults
from opynfield.calculate_measures import coverage_math
from opynfield.config import cov_asymptote
from src.opynfield.calculate_measures.standard_track import StandardTrack

all_tracks = run_all_track_types(test_user_config.groups_and_types, test_user_config.verbose,
                                 test_user_config.arena_radius_cm, test_user_config.running_window_length,
                                 test_user_config.window_step_size, test_user_config.sample_freq,
                                 test_user_config.time_bin_size, test_user_config.trim)


def cartesian_to_polar(x: np.ndarray, y: np.ndarray, verbose: bool) -> tuple[np.ndarray, np.ndarray]:
    # initialize results
    radius = np.zeros(shape=x.shape)
    angle = np.zeros(shape=x.shape)
    # for each point
    for i in range(len(x)):
        # find distance from (0, 0)
        rad = np.sqrt(x[i] ** 2 + y[i] ** 2)
        # find angle from positive x-axis
        theta_radians = np.arctan2(y, x)
        theta_degrees = math.degrees(theta_radians)
        radius[i] = rad
        angle[i] = theta_degrees
    if verbose:
        print('Polar Coordinates Calculated')
    return radius, angle


def step_distance(x: np.ndarray, y: np.ndarray, verbose: bool) -> np.ndarray:
    # initialize results
    act = np.zeros(shape=x.shape)
    # for each point
    for i in range(len(x) - 1):
        # distance is defined between two points, so we will have a trailing zero
        # find the distance between it and the next point
        dx = x[i + 1] - x[i]
        dy = y[i + 1] - y[i]
        dist = np.sqrt(dx ** 2 + dy ** 2)
        act[i] = dist
    if verbose:
        print('Activity Calculated')
    return act


def turning_angle(x: np.ndarray, y: np.ndarray, verbose: bool) -> np.ndarray:
    # initialize results
    turn_ang = np.zeros(shape=x.shape)
    # for each point
    for i in range(len(x) - 2):
        # a turn is defined between two steps or 3 points, so we will have a leading and a trailing zero
        x1 = x[i]
        x2 = x[i + 1]
        x3 = x[i + 2]
        y1 = y[i]
        y2 = y[i + 1]
        y3 = y[i + 2]
        # use law of cosines to get the angle based on the side lengths
        # A is the distance (triangle side length) between previous and current pts
        a = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        # B is the distance (triangle side length) between current and next pts
        b = np.sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2)
        # C is the distance (triangle side length) between previous and next pts
        c = np.sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2)
        # law of cosines: c^2 = a^2 + b^2 - 2abcos(angleC)
        # --> angleC = arccos((a^2 + b^2 - c^2)/(2ab))
        # t1 is numerator
        t1 = (a ** 2) + (b ** 2) - (c ** 2)
        # t2 is denominator
        t2 = a * b * 2
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            # if the fly doesn't move during one of the steps, the triangle is
            # undefined this allows the div by zero to not send warning message
            # bc the arccos (inf) will be nan anyway
            b_mat = t1 / t2
            # if the angle is out of range we want nan to be there instead
            # this silences the warning message about nan
            ta = np.arccos(b_mat)
        # converts from angle C to turn angle
        ta_deg = math.degrees(abs(np.pi - ta))
        # we only care about the magnitude of the turn
        turn_ang[i + 1] = ta_deg  # save to the point where the turn was made
    if verbose:
        print('Turning Angles Calculated')
    return turn_ang


def motion_probabilities(radius: np.ndarray, act: np.ndarray, turn_angle: np.ndarray,
                         inactivity_threshold: float, edge_rad: float, verbose: bool) -> \
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # initialize results
    ppp = np.zeros(shape=radius.shape)
    ppm = np.zeros(shape=radius.shape)
    ppz = np.zeros(shape=radius.shape)
    pzp = np.zeros(shape=radius.shape)
    pzz = np.zeros(shape=radius.shape)

    # all zeros, fill in ones where condition is true
    for i in range(1, len(radius)-1):
        # a motion probability is defined between two steps or 3 points, so we will have a leading and a trailing zero
        if radius[i] >= edge_rad:
            # the turn decision is made inside the edge region
            # (all decisions in the center of the arena do not count towards the motion probabilities)
            step_1 = act[i-1]
            step_2 = act[i]
            if step_1 > inactivity_threshold:
                # will be p plus something
                if step_2 > inactivity_threshold:
                    # will be p plus plus or p plus minus
                    if turn_angle[i] < 90:
                        # considered continuing "straight", so this is p++
                        ppp[i] = 1
                    else:
                        # they turned around
                        ppm[i] = 1
                else:
                    # this is p+0
                    ppz[i] = 1
            else:
                # will be p zero something
                if step_2 > inactivity_threshold:
                    # this is p0+
                    pzp[i] = 1
                else:
                    # this is p00
                    pzz[i] = 1
    if verbose:
        print('Motion Probabilities Calculated')
    return ppp, ppm, ppz, pzp, pzz


def locate_bin(radius: np.ndarray, theta_angle: np.ndarray, node_size: float,
               edge_rad: float, verbose: bool) -> tuple[np.ndarray, float]:
    # initialize bins as -1 (an invalid bin number)
    bins = np.ones(shape=radius.shape) * -1

    num_bins = 360/node_size  # number of bins the arena edge is divided into
    if num_bins < 8:
        raise ValueError('Node Size Too Small')
    for i in range(len(radius)):
        if radius[i] >= edge_rad:
            # the point is in the edge region, so we need to assign it a bin
            bin_i = np.floor(theta_angle[i]/node_size)
            bins[i] = bin_i
    if verbose:
        print('Coverage Bins Located')
    return bins, num_bins


def calculate_coverage(cov_bins: np.ndarray, num_bins: float, verbose: bool) -> np.ndarray:
    # locate_bin has already worried about if the animal is in edge or not, this is just looking at visits and cov
    cov = coverage_math.path_coverage(cov_bins, num_bins)
    if verbose:
        print('Coverage Calculated')
    return cov


def calculate_percent_coverage(cov: np.ndarray, verbose: bool) -> np.ndarray:
    highest_cov = max(cov)
    perc_cov = cov/highest_cov
    if verbose:
        print('Percent Coverage Calculated')
    return perc_cov


def calculate_pica(cov: np.ndarray, asymptote_info: cov_asymptote.CoverageAsymptote,
                   verbose: bool) -> tuple[np.ndarray, float]:
    # format the input data to the fit
    x2 = np.arange(len(cov))
    x1 = np.array(x2)
    y1 = np.array(cov)
    y = y1[~np.isnan(y1)]
    x = x1[~np.isnan(y1)]
    # fit a model to the coverage data
    params = curve_fit(asymptote_info.f_name, x, y, asymptote_info.initial_parameters,
                       bounds=asymptote_info.parameter_bounds, **{'maxfev': asymptote_info.max_f_eval})
    # extract the asymptote value from the model
    asymptote_i = params[asymptote_info.asymptote_param]*asymptote_info.asymptote_sign
    # calculate pica
    pica_i = cov/asymptote_i
    if verbose:
        print('PICA Calculated')
    return pica_i, asymptote_i


def calculate_group_coverage_asymptote(group_tracks: list[StandardTrack],
                                       asymptote_info: cov_asymptote.CoverageAsymptote):
    group_coverage = list()
    group_time = list()
    for track_g in group_tracks:
        for i in range(len(track_g.coverage)):
            group_coverage.append(track_g.coverage[i])
            group_time.append(track_g.t[i])
    x1 = np.array(group_time)
    y1 = np.array(group_coverage)
    y = y1[~np.isnan(y1)]
    x = x1[~np.isnan(y1)]
    params = curve_fit(asymptote_info.f_name, x, y, asymptote_info.initial_parameters,
                       bounds=asymptote_info.parameter_bounds, **{'maxfev': asymptote_info.max_f_eval})
    # extract the asymptote value from the model
    asymptote_g = params[asymptote_info.asymptote_param] * asymptote_info.asymptote_sign
    return asymptote_g


def calculate_pgca(s_track: StandardTrack, asymptote_g: float, verbose: bool):
    s_track.pgca = s_track.coverage/asymptote_g
    s_track.pgca_asymptote = asymptote_g
    if verbose:
        print('PGCA Calculated')
    pass


tracks_by_group = defaultdict(list)
all_standard_tracks = list()
for track in all_tracks:
    assert track.standardized
    # calculate all the independent measures for the track
    r, theta = cartesian_to_polar(track.x, track.y, test_user_config.verbose)
    activity = step_distance(track.x, track.y, test_user_config.verbose)
    turn = turning_angle(track.x, track.y, test_user_config.verbose)
    p_plus_plus, p_plus_minus, p_plus_zero, p_zero_plus, p_zero_zero = motion_probabilities(
        r, activity, turn, test_user_config.inactivity_threshold, test_user_config.set_edge_radius(),
        test_user_config.verbose)
    coverage_bins, n_bins = locate_bin(r, theta, test_defaults.node_size, test_user_config.set_edge_radius(),
                                       test_user_config.verbose)
    coverage = calculate_coverage(coverage_bins, n_bins, test_user_config.verbose)
    percent_coverage = calculate_percent_coverage(coverage, test_user_config.verbose)
    pica, asymptote = calculate_pica(coverage, cov_asymptote.test_cov_asymptote, test_user_config.verbose)
    # save to standard track with all measures as attributes
    standard_track = StandardTrack(track.group, track.x, track.y, track.t, r, theta, activity, turn, p_plus_plus,
                                   p_plus_minus, p_plus_zero, p_zero_plus, p_zero_zero, coverage_bins, n_bins,
                                   coverage, percent_coverage, pica, asymptote)
    all_standard_tracks.append(standard_track)
    # create list of tracks in that group
    tracks_by_group[standard_track.group].append(standard_track)
if test_user_config.verbose:
    print('All Independent Track Measures Calculated')
    print('Tracks Converted To Standard Tracks')
# now find the coverage asymptote for the whole group to get pgca
for g in tracks_by_group:
    group_asymptote = calculate_group_coverage_asymptote(tracks_by_group[g], cov_asymptote.test_cov_asymptote)
    for track in tracks_by_group[g]:
        calculate_pgca(track, group_asymptote, test_user_config.verbose)
