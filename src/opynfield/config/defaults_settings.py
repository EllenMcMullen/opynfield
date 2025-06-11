from dataclasses import dataclass


@dataclass
class Defaults:
    """This dataclass defines many default values that are used across the package.

    Attributes:
        node_size (float): the angle that (when combined with a radial bound) defines a bin for coverage calculations, defaults to 0.1
        save_group_csvs (bool): whether to save a separate .csv file of the component measures for each group, defaults to True
        save_all_group_csvs (bool): whether to save a combined .csv file of the component measures of each group, defaults to True
        save_group_model_csvs (bool): whether to save a separate .csv file of the model parameters for each group, defaults to True
        save_all_group_model_csvs (bool): whether to save a combined .csv file of the model parameters of each group, defaults to True
        n_points_coverage (int): the number of points to group together in an average for the coverage domain, defaults to 36
        n_points_pica (int): the number of points to group together in an average for the pica domain, defaults to 36
        n_points_pgca (int): the number of points to group together in an average for the pgca domain, defaults to 36
        n_bins_percent_coverage (int): the number of points to group together in an average for the percent coverage domain, defaults to 10
        time_averaged_measures (list[str]): which measures should be averaged in the time domain, defaults to ["r", "activity", "p_plus_plus", "p_plus_minus", "p_plus_zero", "p_zero_plus", "p_zero_zero", "coverage", "percent_coverage", "pica", "pgca", "p_plus_plus_given_plus", "p_plus_minus_given_plus", "p_plus_zero_given_plus", "p_zero_plus_given_zero", "p_zero_zero_given_zero", "p_plus_plus_given_any", "p_plus_minus_given_any", "p_plus_zero_given_any", "p_zero_plus_given_any", "p_zero_zero_given_any"]
        coverage_averaged_measures (list[str]): which measures should be averages in the coverage, percent coverage, pica, and pgca domains, defaults to ["activity", "p_plus_plus", "p_plus_minus", "p_plus_zero", "p_zero_plus", "p_zero_zero", "p_plus_plus_given_plus", "p_plus_minus_given_plus", "p_plus_zero_given_plus", "p_zero_plus_given_zero", "p_zero_zero_given_zero", "p_plus_plus_given_any", "p_plus_minus_given_any", "p_plus_zero_given_any", "p_zero_plus_given_any", "p_zero_zero_given_any"]
    """
    # what angle should we use to create the bins for coverage (degrees)
    node_size: float = 0.1
    # should we save out a csv for each group's component measures?
    save_group_csvs: bool = True
    # should we save out a csv with the measures from all the groups in it? (better for stats)
    # save_group_csvs must be true for save_all_group_csvs to be true
    save_all_group_csvs: bool = True
    # should we save a df of the parameters for individuals
    save_group_model_csvs: bool = True
    # should we save a df of the parameters for the individuals from all the groups in it (better for stats)
    save_all_group_model_csvs: bool = True
    # number of points to group together in an average
    n_points_coverage: int = 36
    # number of points to group together in an average
    n_points_pica: int = 36
    # number of points to group together in an average
    n_points_pgca: int = 36
    # number of bins to group together in an average
    n_bins_percent_coverage: int = 10
    # measures to time average (not all measures make sense to average (e.g. angular position))
    time_averaged_measures = [
        "r",
        "activity",
        "p_plus_plus",
        "p_plus_minus",
        "p_plus_zero",
        "p_zero_plus",
        "p_zero_zero",
        "coverage",
        "percent_coverage",
        "pica",
        "pgca",
        "p_plus_plus_given_plus",
        "p_plus_minus_given_plus",
        "p_plus_zero_given_plus",
        "p_zero_plus_given_zero",
        "p_zero_zero_given_zero",
        "p_plus_plus_given_any",
        "p_plus_minus_given_any",
        "p_plus_zero_given_any",
        "p_zero_plus_given_any",
        "p_zero_zero_given_any"
    ]
    coverage_averaged_measures = [
        "activity",
        "p_plus_plus",
        "p_plus_minus",
        "p_plus_zero",
        "p_zero_plus",
        "p_zero_zero",
        "p_plus_plus_given_plus",
        "p_plus_minus_given_plus",
        "p_plus_zero_given_plus",
        "p_zero_plus_given_zero",
        "p_zero_zero_given_zero",
        "p_plus_plus_given_any",
        "p_plus_minus_given_any",
        "p_plus_zero_given_any",
        "p_zero_plus_given_any",
        "p_zero_zero_given_any"
    ]

    def create_pairs(self):
        """Create a list of strings that indicate which measure combinations should be modeled and tested

        :return: list of strings that indicate xy pairs
        :rtype: list[str]
        """
        test_list = []
        for x in ["time", "coverage", "percent_coverage", "pica", "pgca"]:
            if x == "time":
                for y in self.time_averaged_measures:
                    if y != "r":
                        test_list.append(f"{x}_{y}_parameter_")
            else:
                for y in self.coverage_averaged_measures:
                    test_list.append(f"{x}_{y}_parameter_")
        return test_list
