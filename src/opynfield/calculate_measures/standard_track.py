from dataclasses import dataclass, field, fields

import numpy as np
import pandas as pd


@dataclass
class StandardTrack:
    """This dataclass stores all relevant original and derived measures associated with an animal's track. It is
    produced after the track standardization procedure from :func:`tracks_to_measures` is completed.

    Attributes:
        group (str): group to which the track belongs
        x (np.ndarray): the track's x coordinates
        y (np.ndarray): the track's y coordinates
        t (np.ndarray): the time the track's coordinates were recorded
        r (np.ndarray): the track's radial coordinates
        theta (np.ndarray): the track's angular coordinates
        activity (np.ndarray): the track's activity (step length between two consecutive points)
        turn (np.ndarray): the track's turn angle (the angle in degrees that the animal turned between two consecutive steps)
        p_plus_plus (np.ndarray): the raw P++ of the track. See motion probability types for more information.
        p_plus_minus (np.ndarray): the raw P+- of the track. See motion probability types for more information.
        p_plus_zero (np.ndarray): the raw P+0 of the track. See motion probability types for more information.
        p_zero_plus (np.ndarray): the raw P0+ of the track. See motion probability types for more information.
        p_zero_zero (np.ndarray): the raw P00 of the track. See motion probability types for more information.
        coverage_bins (np.ndarray): the bin the animal was in at each tracking point
        n_bins (float): the total number of bins the arena edge is divided into
        coverage (np.ndarray): the raw coverage of the track. See coverage types for more information.
        percent_coverage (np.ndarray): the percent coverage of the track. See coverage types for more information.
        pica (np.ndarray): the PICA (Percent of Individual Coverage Asymptote) of the track. See coverage types for more information.
        pica_asymptote (float): the asymptote of the animals time vs coverage model
        pgca (np.ndarray): the PGCA (Percent of Group Coverage Asymptote) of the group the track belongs to. Or an initialized dummy value of all ones. See coverage types for more information.
        pgca_asymptote (float): the asymptote of the time vs coverage model for the group the track belongs to. Or an initialized dummy value of np.nan
        p_plus_plus_given_plus (np.ndarray): the P++Given+ of the track. See motion probability types for more information.
        p_plus_minus_given_plus (np.ndarray): the P+-Given+ of the track. See motion probability types for more information.
        p_plus_zero_given_plus (np.ndarray): the P+0Given+ of the track. See motion probability types for more information.
        p_zero_plus_given_zero (np.ndarray): the P0+Given0 of the track. See motion probability types for more information.
        p_zero_zero_given_zero (np.ndarray): the P00Given0 of the track. See motion probability types for more information.
        p_plus_plus_given_any (np.ndarray): the P++GivenAny of the track. See motion probability types for more information.
        p_plus_minus_given_any (np.ndarray): the P+-GivenAny of the track. See motion probability types for more information.
        p_plus_zero_given_any (np.ndarray): the P+0GivenAny of the track. See motion probability types for more information.
        p_zero_plus_given_any (np.ndarray): the P0+GivenAny of the track. See motion probability types for more information.
        p_zero_zero_given_any (np.ndarray): the P00GivenAny of the track. See motion probability types for more information.
    """
    # dataclass for standardized track after data is read in and wrangled
    group: str  # can change to enum
    x: np.ndarray = field(repr=False)  # x coordinate
    y: np.ndarray = field(repr=False)  # y coordinate
    t: np.ndarray = field(repr=False)  # time
    r: np.ndarray = field(repr=False)  # radius
    theta: np.ndarray = field(repr=False)  # angular position
    activity: np.ndarray = field(repr=False)  # step distance
    turn: np.ndarray = field(repr=False)  # turn angle
    p_plus_plus: np.ndarray = field(repr=False)  # p++
    p_plus_minus: np.ndarray = field(repr=False)  # p+-
    p_plus_zero: np.ndarray = field(repr=False)  # p+0
    p_zero_plus: np.ndarray = field(repr=False)  # p0+
    p_zero_zero: np.ndarray = field(repr=False)  # p00
    coverage_bins: np.ndarray = field(repr=False)  # bin visited
    n_bins: float  # number of bins
    coverage: np.ndarray = field(repr=False)  # coverage
    percent_coverage: np.ndarray = field(repr=False)  # percent coverage
    pica: np.ndarray = field(repr=False)  # percent of individual coverage asymptote
    pica_asymptote: float  # individual coverage asymptote
    pgca: np.ndarray = field(repr=False)  # percent of group coverage asymptote
    pgca_asymptote: float  # individual coverage asymptote
    p_plus_plus_given_plus: np.ndarray = field(repr=False)  # p++ given +
    p_plus_minus_given_plus: np.ndarray = field(repr=False)  # p+- given +
    p_plus_zero_given_plus: np.ndarray = field(repr=False)  # p+0 given +
    p_zero_plus_given_zero: np.ndarray = field(repr=False)  # p0+ given 0
    p_zero_zero_given_zero: np.ndarray = field(repr=False)  # p00 given 0
    p_plus_plus_given_any: np.ndarray = field(repr=False)  # p++ given any
    p_plus_minus_given_any: np.ndarray = field(repr=False)  # p+- given any
    p_plus_zero_given_any: np.ndarray = field(repr=False)  # p+0 given any
    p_zero_plus_given_any: np.ndarray = field(repr=False)  # p0+ given any
    p_zero_zero_given_any: np.ndarray = field(repr=False)  # p00 given any

    @classmethod
    def to_dataframes(
        cls: "StandardTrack",
        instances: list["StandardTrack"],
        extra_fields_by_name: list[str],
    ) -> tuple[dict[str, pd.DataFrame], list[str]]:
        """This class method, called in :func:`individual_measures_to_dfs`, will create a dataframe for each dataclass
        attribute that is either an array or is included in the 'extra_fields_by_name' argument.

        :param instances: list of the standard tracks to be summarized together (usually all tracks belonging to the
            same group)
        :type instances: list[StandardTrack]
        :param extra_fields_by_name: which non-array fields also need to be stored in dataframes
        :type extra_fields_by_name: list[str]
        :return: a tuple of a dictionary of field names to dataframes and a list of all the field  names
        :rtype: tuple[dict[str, pd.DataFrame], list[str]]
        """
        # make sure we are giving it a list of standard tracks for instances
        assert all(isinstance(i, StandardTrack) for i in instances)
        # TODO: Check validity of `extra_fields_by_name`
        # get the names of all the fields of standard track
        all_fields = fields(cls)
        # since we want to save the np array ones, get list of just those that are np arrays
        array_fields_names = [f.name for f in all_fields if f.type == np.ndarray]
        # add any additional fields we want to make a df from (like pica or pgca asymptote)
        fields_to_dataframe = array_fields_names + extra_fields_by_name
        # initialize a place to store the dfs in a dict by key = name of attribute
        all_dataframes: dict[str, pd.DataFrame] = {}
        for f in fields_to_dataframe:
            # for each field we want a df from
            arrays = [getattr(i, f) for i in instances]
            # get that field from every instance and put it in a df
            all_dataframes[f] = pd.DataFrame(arrays)
            # save that df to the dict with the field name as key
        return all_dataframes, fields_to_dataframe

    def set_pgca(self, input_pgca: np.ndarray, input_pgca_a: float):
        """This is a method that re-sets the pgca and pgca_asymptote values from their dummy initialization values to
        their true values calculated during the track standardization procedure.

        :param input_pgca: the PGCA (Percent of Group Coverage Asymptote) of the group the track belongs to. See
            coverage types for more information.
        :type input_pgca: np.ndarray
        :param input_pgca_a: the asymptote of the time vs coverage model for the group the track belongs to
        :type input_pgca_a: float
        """
        self.pgca = input_pgca
        self.pgca_asymptote = input_pgca_a
