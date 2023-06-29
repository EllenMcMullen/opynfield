from dataclasses import dataclass


@dataclass
class Defaults:
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
        "p_zero_zero_given_any",
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
        "p_zero_zero_given_any",
    ]

    def create_pairs(self):
        test_list = []
        for x in ["time", "coverage", "pica", "pgca", "percent_coverage"]:
            if x == "time":
                for y in self.time_averaged_measures:
                    if y != "r":
                        test_list.append(f"{x}_{y}_parameter_")
            else:
                for y in self.coverage_averaged_measures:
                    test_list.append(f"{x}_{y}_parameter_")
        return test_list
