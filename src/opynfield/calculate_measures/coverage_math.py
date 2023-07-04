import numpy as np
import numba as nb


def path_coverage(cov_bins: np.ndarray, num_bins: float) -> np.ndarray:
    """This function formats inputs and calls `_path_coverage` to calculate the animal's coverage over time.

    :param cov_bins: which bin the animal is located in at each tracking point
    :type cov_bins: np.ndarray
    :param num_bins: the total number of bins the arena edge region is divided into
    :type num_bins: float
    :return: the coverage of the animal at each tracking point
    :rtype: np.ndarray
    """
    # convert to int to run the actual coverage function
    bins = cov_bins.astype("int")
    m = int(num_bins)
    return _path_coverage(bins, m)


@nb.jit(fastmath=True, nopython=True)
def _path_coverage(fbl: np.ndarray, num_bins: int) -> np.ndarray:
    """This function orchestrates the calculation of an animal's coverage at each tracking point. It first identifies
    the initial bin, then at each time point updates how many times each bin has been visited. From the visits at each
    bin the coverage is calculated at each time point.

    :param fbl: fly bin location - which bin the animal is located in at each tracking point
    :type fbl: np.ndarray
    :param num_bins: the total number of bins the arena edge region is divided into
    :type num_bins: int
    :return: the coverage of the animal at each tracking point
    :rtype: np.ndarray
    """
    initial_visits = np.zeros(num_bins, dtype=np.int16)
    # list of visits by bin (start at all 0)
    first_visits = update_first_visit(initial_visits, fbl[0])
    # add 1 to the bin the fly starts in
    # if fly is not at edge do nothing
    prev_visits = first_visits
    t_end = len(fbl)
    cov = np.zeros(t_end)
    # coverage at the first time point will either be 0 or 1/num_bins
    cov[0] = fly_coverage(first_visits, num_bins)
    for t in range(1, t_end):
        # skips the first point because taken care of above
        # fbl[t-1] is previous bin
        # fbl[t] is new bin
        # prev_visits is the un-updated list of number of visits to each bin
        # current_visits is the updated list of number of visits to each bin
        current_visits = update_visits(fbl[t - 1], fbl[t], prev_visits, num_bins)
        # if fly is still in edge, add one to the bin the fly visits next, plus all the bins traversed to get there
        # if fly leaves edge do nothing
        # if fly enters the edge add one to current bin

        # calculates the coverage at that time point
        cov[t] = fly_coverage(current_visits, num_bins)
        prev_visits = current_visits
    return cov


@nb.jit(fastmath=True, nopython=True)
def update_first_visit(visits: np.ndarray, first_vis: int) -> np.ndarray:
    """Creates a bin visit array for the initial time point.

    :param visits: bin visit array initialized with 0s
    :type visits: np.ndarray
    :param first_vis: bin the animal was in for the first tracking point
    :type first_vis: int
    :return: bin visit array updated with the first bin
    :rtype: np.ndarray
    """
    if first_vis != -1:
        # -1 if not in the edge region
        # fist_vis is the bin at the first time point
        visits[first_vis] += 1
    else:
        pass
    return visits


@nb.jit(fastmath=True, nopython=True)
def fly_coverage(visits: np.ndarray, m: int) -> np.ndarray:
    """Calculates the coverage of a tracking point from a bin visit array and assigns the coverage value to the coverage
        array at that index.

    :param visits: bin visit array at a tracking point
    :type visits: np.ndarray
    :param m: number of total bins
    :type m: int
    :return: an array of coverage at each tracking point, updated up to the current tracking point
    :rtype: np.ndarray
    """
    # number of visits to all bins
    # noinspection PyArgumentList
    min_visits = visits.min()
    # fraction of bins that have been visited more than that
    frac_more_than_min = (visits > min_visits).sum() / m
    v_new = min_visits + frac_more_than_min
    return v_new


@nb.jit(fastmath=True, nopython=True)
def update_visits(
    past_fly_bin: int, current_fly_bin: int, past_visits: np.ndarray, m: int
) -> np.ndarray:
    """Determines if the bin visit array needs to be updated with information from the current bin location, or if the
    bin visit counts remain unchanged. Calls :func:`update_visits_for_steps_between_bins` the bin visit array needs
    multiple updates.

    :param past_fly_bin: the bin the animal was in at the previous tracking point
    :type past_fly_bin: int
    :param current_fly_bin: the bin that the animal is in at the current tracking point
    :type current_fly_bin: int
    :param past_visits: the bin visit array at the previous tracking point
    :type past_visits: np.ndarray
    :param m: number of total bins
    :type m: int
    :return: the bin visit array at the current tracking point
    :rtype: np.ndarray
    """
    if current_fly_bin == -1 or past_fly_bin == current_fly_bin:
        # the fly left the edge, or did not move, visits did not change
        return past_visits
    elif past_fly_bin == -1:
        # the fly is entering the edge, only can assign a visit to the current bin
        past_visits[current_fly_bin] += 1
        return past_visits
    # Here we know that current_fly_bin and past_fly_bin are valid unique
    # bins between 1 and M

    # all other flies have traversed between bins
    v_new = update_visits_for_steps_between_bins(
        past_fly_bin, current_fly_bin, past_visits, m
    )
    return v_new


@nb.jit(fastmath=True, nopython=True)
def update_visits_for_steps_between_bins(
    past_fly_bin: int, current_fly_bin: int, past_visits: np.ndarray, m: int
) -> np.ndarray:
    """Updates the bin visit array in cases where the animal has traversed across multiple bins in a single step by
    identifying the direction of travel, the number of bins traversed, and the specific bins that were visited during
    the travel between bins

    :param past_fly_bin: the bin the animal was in at the previous tracking point
    :type past_fly_bin: int
    :param current_fly_bin: the bin that the animal is in at the current tracking point
    :type current_fly_bin: int
    :param past_visits: the bin visit array at the previous tracking point
    :type past_visits: np.ndarray
    :param m: number of total bins
    :type m: int
    :return: the bin visit array at the current tracking point
    :rtype: np.ndarray
    """
    # figure out what direction the fly is moving, and how many steps
    step_direction, steps_taken = sign_to_step(past_fly_bin, current_fly_bin, m)
    # step direction (-1 = clockwise, 1 = counterclockwise), steps taken = # taken

    # figure out what bins were traversed (list of bin numbers)
    bins_traveled = bins_traversed(past_fly_bin, steps_taken, step_direction, m)

    # add one to all the bins traversed
    past_visits[bins_traveled] += 1
    return past_visits


@nb.jit(fastmath=True, nopython=True)
def sign_to_step(
    past_fly_bin: int, current_fly_bin: int, num_bins: int
) -> tuple[int, int]:
    """Identifies the direction of travel and the number of bins traversed in that direction.

    :param past_fly_bin: the bin the animal was in at the previous tracking point
    :type past_fly_bin: int
    :param current_fly_bin: the bin that the animal is in at the current tracking point
    :type current_fly_bin: int
    :param num_bins: number of total bins
    :type num_bins: int
    :return: tuple of the direction the animal is traveling (1 if counterclockwise, -1 if clockwise), and the number of
        bins the animal traversed in that direction of travel
    :rtype: tuple[int, int]
    """
    # figure out which way the fly is moving
    simple_step_number = abs(past_fly_bin - current_fly_bin)
    complement_step_number = num_bins - simple_step_number
    steps_to_take = min(simple_step_number, complement_step_number)
    # assume fly walked the shorter direction between bins
    if simple_step_number == steps_to_take:
        # did not cross the modular boundary
        if current_fly_bin > past_fly_bin:
            # fly moved counterclockwise
            return 1, steps_to_take
        else:
            # fly moved clockwise
            return -1, steps_to_take
    else:
        # fly crossed the modular boundary
        if current_fly_bin > past_fly_bin:
            # fly moved clockwise
            return -1, steps_to_take
        else:
            # fly moved counterclockwise
            return 1, steps_to_take


@nb.jit(fastmath=True, nopython=True)
def bins_traversed(past_fly_bin: int, n_steps: int, step_direction: int, m) -> np.ndarray:
    """Identifies which bins were visited along a path of ``n_steps`` from the current bin in the ``step_direction``.

    :param past_fly_bin: the bin the animal was in at the previous tracking point
    :type past_fly_bin: int
    :param n_steps: the number of bins the animal traversed
    :type n_steps: int
    :param step_direction: the direction the animal is traveling (1 if counterclockwise, -1 if clockwise)
    :type step_direction: int
    :param m: number of total bins
    :type m: int
    :return: which bins were visited along the path
    :rtype: np.ndarray
    """
    start = (
        past_fly_bin + step_direction
    )  # don't count the bin that was already visited
    end = (
        past_fly_bin + (step_direction * n_steps) + step_direction
    )  # count up in the right direction
    visits_added = (
        np.arange(start, end, step_direction) % m
    )  # make it modular if it passes the 0th bin
    # visits added is a list of bin numbers
    return visits_added
