from dataclasses import dataclass, field, fields

import numpy as np
import pandas as pd


@dataclass
class StandardTrack:
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
    def to_dataframes(cls: "StandardTrack", instances: list["StandardTrack"],
                      extra_fields_by_name: list[str]) -> tuple[dict[str, pd.DataFrame], list[str]]:
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

    def set_pgca(self, input_pgca, input_pgca_a):
        self.pgca = input_pgca
        self.pgca_asymptote = input_pgca_a
