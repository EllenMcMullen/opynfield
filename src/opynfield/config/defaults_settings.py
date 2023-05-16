from dataclasses import dataclass


@dataclass
class Defaults:
    # what angle should we use to create the bins for coverage (degrees)
    node_size: float = 0.1
    # should we save out a csv for each group's component measures?
    save_group_csvs: bool = True
    # should we save out a csv with the measures from all the groups in it? (better for stats)
    save_all_group_csvs: bool = True
    # measures to time average (not all measures make sense to average (e.g. angular position))
    time_averaged_measures = ['r', 'activity', 'p_plus_plus', 'p_plus_minus', 'p_plus_zero', 'p_zero_plus',
                              'p_zero_zero', 'coverage', 'percent_coverage', 'pica', 'pgca', 'p_plus_plus_given_plus',
                              'p_plus_minus_given_plus', 'p_plus_zero_given_plus', 'p_zero_plus_given_zero',
                              'p_zero_zero_given_zero', 'p_plus_plus_given_any', 'p_plus_minus_given_any',
                              'p_plus_zero_given_any', 'p_zero_plus_given_any', 'p_zero_zero_given_any']
