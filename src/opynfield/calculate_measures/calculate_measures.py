import numpy as np
import math
import warnings
from scipy.optimize import curve_fit
from collections import defaultdict
from opynfield.config.user_input import UserInput
from opynfield.config.defaults_settings import Defaults
from opynfield.calculate_measures import coverage_math
from opynfield.config.cov_asymptote import CoverageAsymptote
from opynfield.readin.track import Track
from opynfield.calculate_measures.standard_track import StandardTrack


def cartesian_to_polar(
    x: np.ndarray, y: np.ndarray, verbose: bool
) -> tuple[np.ndarray, np.ndarray]:
    """ This function converts an animal's tracking coordinates from cartesian to polar coordinates.
    It is one step in the track standardization procedure orchestrated
    by :func:`opynfield.calculate_measures.calculate_measures.tracks_to_measures`

    :param x: the x coordinates of a :class:`opynfield.readin.track.Track` object
    :type x: np.ndarray
    :param y: the y coordinates of a :class:`opynfield.readin.track.Track` object
    :type y: np.ndarray
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: a tuple of the r and theta coordinates of the :class:`opynfield.readin.track.Track`
    :rtype: tuple[np.ndarray, np.ndarray]
    """

    # initialize results
    radius = np.zeros(shape=x.shape)
    angle = np.zeros(shape=x.shape)
    # for each point
    for i in range(len(x)):
        # find distance from (0, 0)
        rad = np.sqrt(x[i] ** 2 + y[i] ** 2)
        # find angle from positive x-axis
        theta_radians = np.arctan2(y[i], x[i])
        theta_degrees = math.degrees(theta_radians)
        radius[i] = rad
        angle[i] = theta_degrees
    if verbose:
        print("Polar Coordinates Calculated")
    return radius, angle


def step_distance(x: np.ndarray, y: np.ndarray, verbose: bool) -> np.ndarray:
    """This function calculates the distance between each consecutive pair of tracking coordinates of an animal.
    It is one step in the track standardization procedure orchestrated
    by :func:`opynfield.calculate_measures.calculate_measures.tracks_to_measures`

    :param x: the x coordinates of a :class:`opynfield.readin.track.Track` object
    :type x: np.ndarray
    :param y: the y coordinates of a :class:`opynfield.readin.track.Track` object
    :type y: np.ndarray
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: the distance stepped between tracking points (also called 'activity')
    :rtype: np.ndarray
    """
    # initialize results
    act = np.zeros(shape=x.shape)
    # for each point
    for i in range(len(x) - 1):
        # distance is defined between two points, so we will have a trailing zero
        # find the distance between it and the next point
        dx = x[i + 1] - x[i]
        dy = y[i + 1] - y[i]
        dist = np.sqrt(dx**2 + dy**2)
        act[i] = dist
    if verbose:
        print("Activity Calculated")
    return act


def turning_angle(x: np.ndarray, y: np.ndarray, verbose: bool) -> np.ndarray:
    """This function calculates the angle that the animal turned between two consecutive steps,
    using the law of cosines. It is one step in the track standardization procedure orchestrated
    by :func:`opynfield.calculate_measures.calculate_measures.tracks_to_measures`

    :param x: the x coordinates of a :class:`opynfield.readin.track.Track` object
    :type x: np.ndarray
    :param y: the y coordinates of a :class:`opynfield.readin.track.Track` object
    :type y: np.ndarray
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: the magnitude of the angle (in degrees) from a straight heading that the animal turned between
        each consecutive set of steps.
    :rtype: np.ndarray
    """
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
        t1 = (a**2) + (b**2) - (c**2)
        # t2 is denominator
        t2 = a * b * 2
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
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
        print("Turning Angles Calculated")
    return turn_ang


def motion_probabilities(
    radius: np.ndarray,
    act: np.ndarray,
    turn_angle: np.ndarray,
    inactivity_threshold: float,
    edge_rad: float,
    verbose: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """This function calculates P++, P+-, P+0, P0+, and P00 (collectively 'motion probabilities')
    from an animal's track trajectory. See motion probability types for more information. It is one step in the track
    standardization procedure orchestrated
    by :func:`opynfield.calculate_measures.calculate_measures.tracks_to_measures`

    :param radius: the radial position of the animal at each tracking point
    :type radius: np.ndarray
    :param act: the length of the step taken by the animal between two points
    :type act: np.ndarray
    :param turn_angle: the angle the animal turned at each point between two steps
    :type turn_angle: np.ndarray
    :param inactivity_threshold: to account for body wobble, how small of a step length do we consider to be
        negligible and set to zero - sourced from :class:`opynfield.config.user_input.UserInput` object
    :type inactivity_threshold: np.ndarray
    :param edge_rad: to consider the motion probabilities only near the edge of the arena, at what radius do we consider
        the animal to be in the edge region - sourced from :class:`opynfield.config.user_input.UserInput` object
    :type edge_rad: np.ndarray
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: tuple of the raw data for motion probabilities (P++, P+-, P+0, P0+, P00) - 1 where the action occurred and
        0 elsewhere
    :rtype: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    """
    # initialize results
    ppp = np.zeros(shape=radius.shape)
    ppm = np.zeros(shape=radius.shape)
    ppz = np.zeros(shape=radius.shape)
    pzp = np.zeros(shape=radius.shape)
    pzz = np.zeros(shape=radius.shape)

    # all zeros, fill in ones where condition is true
    for i in range(1, len(radius) - 1):
        # a motion probability is defined between two steps or 3 points, so we will have a leading and a trailing zero
        if radius[i] >= edge_rad:
            # the turn decision is made inside the edge region
            # (all decisions in the center of the arena do not count towards the motion probabilities)
            step_1 = act[i - 1]
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
        print("Motion Probabilities Calculated")
    return ppp, ppm, ppz, pzp, pzz


def locate_bin(
    radius: np.ndarray,
    theta_angle: np.ndarray,
    node_size: float,
    edge_rad: float,
    verbose: bool,
) -> tuple[np.ndarray, float]:
    """This function assigns a bin number to each tracking point of an animal to facilitate the calculation of coverage.
    It is one step in the track standardization procedure orchestrated
    by :func:`opynfield.calculate_measures.calculate_measures.tracks_to_measures`

    :param radius: the radial position of the animal at each tracking point
    :type radius: np.ndarray
    :param theta_angle: the angular position of the animal at each tracking point
    :type theta_angle: np.ndarray
    :param node_size: the angle that (when combined with ``edge_rad``) defines a bin - sourced from
        :class:`opynfield.config.user_input.UserInput`
    :type node_size: float
    :param edge_rad: at what radius do we consider the animal to be in the edge region, when combined with ``node_size``
        this defines a bin - sourced from :class:`opynfield.config.user_input.UserInput`
    :type edge_rad: float
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: tuple of the bin assignment array and the total number of bins used to make the assignment
    :rtype: tuple[np.ndarray, float]
    """
    # initialize bins as -1 (an invalid bin number)
    bins = np.ones(shape=radius.shape) * -1

    num_bins = 360 / node_size  # number of bins the arena edge is divided into
    if num_bins < 8:
        raise ValueError("Node Size Too Small")
    for i in range(len(radius)):
        if radius[i] >= edge_rad:
            # the point is in the edge region, so we need to assign it a bin
            bin_i = np.floor(theta_angle[i] / node_size)
            bins[i] = bin_i
    if verbose:
        print("Coverage Bins Located")
    return bins, num_bins


def calculate_coverage(
    cov_bins: np.ndarray, num_bins: float, verbose: bool
) -> np.ndarray:
    """This function is calls functions from the coverage_math module to calculate the animal's coverage over time.
    See coverage types for comparison of (raw) coverage to other coverage measures.
    It is one step in the track standardization procedure orchestrated
    by :func:`opynfield.calculate_measures.calculate_measures.tracks_to_measures`

    :param cov_bins: which bin the animal is located in at each tracking point
    :type cov_bins: np.ndarray
    :param num_bins: the total number of bins the arena edge region is divided into
    :type num_bins: float
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: the coverage of the animal at each tracking point
    :rtype: np.ndarray
    """
    # locate_bin has already worried about if the animal is in edge or not, this is just looking at visits and cov
    cov = coverage_math.path_coverage(cov_bins, num_bins)
    if verbose:
        print("Coverage Calculated")
    return cov


def calculate_percent_coverage(cov: np.ndarray, verbose: bool) -> np.ndarray:
    """This function normalizes an animal's coverage by the maximum coverage the animal reaches to get its percent
    coverage. See coverage types for comparison of percent coverage to other coverage measures.
    It is one step in the track standardization procedure orchestrated
    by :func:`opynfield.calculate_measures.calculate_measures.tracks_to_measures`

    :param cov: the coverage of the animal at each tracking point
    :type cov: np.ndarray
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: the percent coverage (normalized coverage) of the animal at each tracking point
    :rtype: np.ndarray
    """
    highest_cov = max(cov)
    perc_cov = cov / highest_cov
    if verbose:
        print("Percent Coverage Calculated")
    return perc_cov


def calculate_pica(
    cov: np.ndarray, asymptote_info: CoverageAsymptote, verbose: bool
) -> tuple[np.ndarray, float]:
    """This function normalizes an animal's coverage by its predicted coverage asymptote from the time vs coverage
    model. See coverage types for comparison of PICA to other coverage measures.
    It is one step in the track standardization procedure orchestrated
    by :func:`opynfield.calculate_measures.calculate_measures.tracks_to_measures`

    :param cov: the coverage of the animal at each tracking point
    :type cov: np.ndarray
    :param asymptote_info: a custom dataclass that includes information needed to calculate the animal's
        coverage asymptote
    :type asymptote_info: CoverageAsymptote
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: the PICA (Percent of Individual Coverage Asymptote) of the animal at each tracking point
    :rtype: np.ndarray
    """
    # format the input data to the fit
    x2 = np.arange(len(cov))
    x1 = np.array(x2)
    y1 = np.array(cov)
    y = y1[~np.isnan(y1)]
    x = x1[~np.isnan(y1)]
    # fit a model to the coverage data
    # noinspection PyTupleAssignmentBalance
    params, cv = curve_fit(
        asymptote_info.f_name,
        x,
        y,
        p0=asymptote_info.initial_parameters,
        bounds=asymptote_info.parameter_bounds,
        **{"maxfev": asymptote_info.max_f_eval}
    )
    # extract the asymptote value from the model
    asymptote_i = params[asymptote_info.asymptote_param] * asymptote_info.asymptote_sign
    # calculate pica
    pica_i = cov / asymptote_i
    if verbose:
        print("PICA Calculated")
    return pica_i, asymptote_i


def calculate_group_coverage_asymptote(
    group_tracks: list[StandardTrack], asymptote_info: CoverageAsymptote
) -> float:
    """This function calculates the coverage asymptote of a group based on the aggregated data from all
    individuals in the group.

    :param group_tracks: a list of all standardized tracks belonging to the same analysis group
    :type group_tracks: list[StandardTrack]
    :param asymptote_info: a custom dataclass that includes information needed to calculate the group's
        coverage asymptote
    :type asymptote_info: CoverageAsymptote
    :return: the group's coverage asymptote to be used in calculating the PGCA of individuals in that group
    :rtype: float
    """
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
    # noinspection PyTupleAssignmentBalance
    params, cv = curve_fit(
        asymptote_info.f_name,
        x,
        y,
        asymptote_info.initial_parameters,
        bounds=asymptote_info.parameter_bounds,
        **{"maxfev": asymptote_info.max_f_eval}
    )
    # extract the asymptote value from the model
    asymptote_g = params[asymptote_info.asymptote_param] * asymptote_info.asymptote_sign
    return asymptote_g


def calculate_pgca(s_track: StandardTrack, asymptote_g: float, verbose: bool):
    """This function normalizes an animal's coverage by its group's predicted coverage asymptote from the time vs
    coverage model. It also sets the group asymptote as an attribute of the track.
    This must occur after all tracks are standardized and group coverage asymptotes are calculated.
    See coverage types for comparison of PGCA to other coverage measures.

    :param s_track: a standardized track
    :type s_track: StandardTrack
    :param asymptote_g: the group coverage asymptote for the group to which the s_track belongs
        coverage asymptote
    :type asymptote_g: float
    :param verbose: display progress update, sourced from :class:`opynfield.config.user_input.UserInput` object
    :type verbose: bool
    :return: the PGCA (Percent of Group Coverage Asymptote) of the animal at each tracking point
    :rtype: np.ndarray
    """
    track_pgca = s_track.coverage / asymptote_g
    s_track.set_pgca(track_pgca, asymptote_g)
    if verbose:
        print("PGCA Calculated")
    pass


def motion_probabilities_given_previous(
    ppp: np.ndarray, ppm: np.ndarray, ppz: np.ndarray, pzp: np.ndarray, pzz: np.ndarray
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray
]:
    """This function calculates P++Given+, P+-Given+, P+0Given+, P0+Given0, P00Given0, P++GivenAny, P+-GivenAny,
    P+0GivenAny, P0+GivenAny, and P00GivenAny (collectively 'motion probabilities given previous'). See motion
    probability types for more information. It is one step in the track standardization procedure orchestrated
    by :func:`opynfield.calculate_measures.calculate_measures.tracks_to_measures`

    :param ppp: the raw P++ values from :func:`opynfield.calculate_measures.calculate_measures.motion_probabilities`
    :type ppp: np.ndarray
    :param ppm: the raw P+- values from :func:`opynfield.calculate_measures.calculate_measures.motion_probabilities`
    :type ppm: np.ndarray
    :param ppz: the raw P+0 values from :func:`opynfield.calculate_measures.calculate_measures.motion_probabilities`
    :type ppz: np.ndarray
    :param pzp: the raw P0+ values from :func:`opynfield.calculate_measures.calculate_measures.motion_probabilities`
    :type pzp: np.ndarray
    :param pzz: the raw P00 values from :func:`opynfield.calculate_measures.calculate_measures.motion_probabilities`
    :type pzz: np.ndarray
    :return: the motion probabilities given previous - 1 where the action occurred, 0 where it
        could have occurred but didn't, and np.nan elsewhere.
    :rtype: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray,
        np.ndarray, np.ndarray]
    """
    # take the 'raw' motion probs (zero everywhere but one where mp occurred)
    # convert to given plus, given zero, and given any formats
    # np.nans everywhere, 1 where mp occurred, 0 where mp could have occurred

    # previous steps
    given_plus = ppp + ppm + ppz
    given_zero = pzp + pzz
    given_any = given_plus + given_zero

    # ppp given plus should first 0 where given_plus is true and np.nan where it is not
    # then it should be 1 where ppp is true and 0/nan (ppp given plus) where not
    pppgp = np.where(given_plus == 1, 0, np.nan)
    pppgp = np.where(ppp == 1, 1, pppgp)
    # ppm given plus should first 0 where given_plus is true and np.nan where it is not
    # then it should be 1 where ppm is true and 0/nan (ppm given plus) where not
    ppmgp = np.where(given_plus == 1, 0, np.nan)
    ppmgp = np.where(ppm == 1, 1, ppmgp)
    # ppz given plus should first 0 where given_plus is true and np.nan where it is not
    # then it should be 1 where ppz is true and 0/nan (ppz given plus) where not
    ppzgp = np.where(given_plus == 1, 0, np.nan)
    ppzgp = np.where(ppz == 1, 1, ppzgp)
    # pzp given zero should first 0 where given_zero is true and np.nan where it is not
    # then it should be 1 where pzp is true and 0/nan (pzp given zero) where not
    pzpgz = np.where(given_zero == 1, 0, np.nan)
    pzpgz = np.where(pzp == 1, 1, pzpgz)
    # pzz given zero should first 0 where given_zero is true and np.nan where it is not
    # then it should be 1 where pzz is true and 0/nan (pzz given zero) where not
    pzzgz = np.where(given_zero == 1, 0, np.nan)
    pzzgz = np.where(pzz == 1, 1, pzzgz)

    # ppp given any should first 0 where given_any is true and np.nan where it is not
    # then it should be 1 where ppp is true and 0/nan (ppp given any) where not
    pppga = np.where(given_any == 1, 0, np.nan)
    pppga = np.where(ppp == 1, 1, pppga)
    # ppm given any should first 0 where given_any is true and np.nan where it is not
    # then it should be 1 where ppm is true and 0/nan (ppm given any) where not
    ppmga = np.where(given_any == 1, 0, np.nan)
    ppmga = np.where(ppm == 1, 1, ppmga)
    # ppz given any should first 0 where given_any is true and np.nan where it is not
    # then it should be 1 where ppz is true and 0/nan (ppz given any) where not
    ppzga = np.where(given_any == 1, 0, np.nan)
    ppzga = np.where(ppz == 1, 1, ppzga)
    # pzp given any should first 0 where given_any is true and np.nan where it is not
    # then it should be 1 where pzp is true and 0/nan (pzp given any) where not
    pzpga = np.where(given_any == 1, 0, np.nan)
    pzpga = np.where(pzp == 1, 1, pzpga)
    # pzz given any should first 0 where given_any is true and np.nan where it is not
    # then it should be 1 where pzz is true and 0/nan (pzz given any) where not
    pzzga = np.where(given_any == 1, 0, np.nan)
    pzzga = np.where(pzz == 1, 1, pzzga)
    return pppgp, ppmgp, ppzgp, pzpgz, pzzgz, pppga, ppmga, ppzga, pzpga, pzzga


def tracks_to_measures(
    all_tracks: list[Track],
    user_config: UserInput,
    default_settings: Defaults,
    coverage_settings: CoverageAsymptote,
) -> tuple[list[StandardTrack], defaultdict[str, list[StandardTrack]]]:
    """This function runs the entire standardization procedure to transform a Track to a StandardTrack. It runs the
    procedure for a list of all tracks in the analysis.

    :param all_tracks: list of all the tracks read in for analysis
    :type all_tracks: list[Track]
    :param user_config: a custom dataclass that contains user inputs for analysis
    :type user_config: UserInput
    :param default_settings: a custom dataclass that contains default settings for analysis
    :type default_settings: Defaults
    :param coverage_settings: a custom class that contains settings for the calculation of coverage asymptotes
    :type coverage_settings: CoverageAsymptote
    :return: tuple of  a list of all standardized tracks and a dictionary of group names to a list of all standardized
        tracks belonging to that group
    :rtype: tuple[list[StandardTrack], defaultdict[str, list[StandardTrack]]]
    """
    tracks_by_group = defaultdict(list)
    all_standard_tracks = list()
    for track in all_tracks:
        assert track.standardized
        # calculate all the independent measures for the track
        r, theta = cartesian_to_polar(track.x, track.y, user_config.verbose)
        activity = step_distance(track.x, track.y, user_config.verbose)
        turn = turning_angle(track.x, track.y, user_config.verbose)
        (
            p_plus_plus,
            p_plus_minus,
            p_plus_zero,
            p_zero_plus,
            p_zero_zero,
        ) = motion_probabilities(
            r,
            activity,
            turn,
            user_config.inactivity_threshold,
            user_config.set_edge_radius(),
            user_config.verbose,
        )
        (
            p_plus_plus_given_plus,
            p_plus_minus_given_plus,
            p_plus_zero_given_plus,
            p_zero_plus_given_zero,
            p_zero_zero_given_zero,
            p_plus_plus_given_any,
            p_plus_minus_given_any,
            p_plus_zero_given_any,
            p_zero_plus_given_any,
            p_zero_zero_given_any,
        ) = motion_probabilities_given_previous(
            p_plus_plus, p_plus_minus, p_plus_zero, p_zero_plus, p_zero_zero
        )
        coverage_bins, n_bins = locate_bin(
            r,
            theta,
            default_settings.node_size,
            user_config.set_edge_radius(),
            user_config.verbose,
        )
        coverage = calculate_coverage(coverage_bins, n_bins, user_config.verbose)
        percent_coverage = calculate_percent_coverage(coverage, user_config.verbose)
        pica, asymptote = calculate_pica(
            coverage, coverage_settings, user_config.verbose
        )
        # save to standard track with all measures as attributes
        # initialize the pgca as ones and np.nan until they are calculated
        standard_track = StandardTrack(
            track.group,
            track.x,
            track.y,
            track.t,
            r,
            theta,
            activity,
            turn,
            p_plus_plus,
            p_plus_minus,
            p_plus_zero,
            p_zero_plus,
            p_zero_zero,
            coverage_bins,
            n_bins,
            coverage,
            percent_coverage,
            pica,
            asymptote,
            np.ones(shape=pica.shape),
            np.nan,
            p_plus_plus_given_plus,
            p_plus_minus_given_plus,
            p_plus_zero_given_plus,
            p_zero_plus_given_zero,
            p_zero_zero_given_zero,
            p_plus_plus_given_any,
            p_plus_minus_given_any,
            p_plus_zero_given_any,
            p_zero_plus_given_any,
            p_zero_zero_given_any,
        )
        all_standard_tracks.append(standard_track)
        # create list of tracks in that group
        tracks_by_group[standard_track.group].append(standard_track)
    if user_config.verbose:
        print("All Independent Track Measures Calculated")
        print("Tracks Converted To Standard Tracks")
    # now find the coverage asymptote for the whole group to get pgca
    for g in tracks_by_group:
        # this group's asymptote
        group_asymptote = calculate_group_coverage_asymptote(
            tracks_by_group[g], coverage_settings
        )
        for track in tracks_by_group[g]:
            # use the group's asymptote to calculate pgca for each track in that group
            calculate_pgca(track, group_asymptote, user_config.verbose)
    return all_standard_tracks, tracks_by_group
