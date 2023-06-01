from src.opynfield.config.user_input import UserInput
from src.opynfield.readin.run_all import run_all_track_types
from src.opynfield.config.defaults_settings import Defaults
from src.opynfield.config.cov_asymptote import CoverageAsymptote
from src.opynfield.calculate_measures.calculate_measures import tracks_to_measures
from src.opynfield.summarize_measures.summarize_individuals import individual_measures_to_dfs
from src.opynfield.summarize_measures.summarize_groups import time_average, cov_measure_average,\
    percent_coverage_average
from src.opynfield.config.model_settings import set_up_fits
from src.opynfield.fit_models.fit_individual_models import fit_all, find_fit_bounds, re_fit_all


def run():
    # create your user config settings
    user_config = UserInput({'Canton S': ['Buridian Tracker'], 'Canton S 2': ['Buridian Tracker']},
                            {'Canton S': 'CS1', 'Canton S 2': 'CS2'}, 4.2, 30, 1, 1, 0.001, True,
                            '/Users/ellenmcmullen/Desktop/TestRunResults')
    user_config.prep_directory()
    # read in the data
    track_list = run_all_track_types(user_config.groups_and_types, user_config.verbose, user_config.arena_radius_cm,
                                     user_config.running_window_length, user_config.window_step_size,
                                     user_config.sample_freq, user_config.time_bin_size, user_config.trim)
    # set the default parameters (or override)
    test_defaults = Defaults()
    # identify functional form for PICA and PGCA (or override)
    test_cov_asymptote = CoverageAsymptote()
    # calculate measures from track data
    standard_tracks, tracks_by_groups = tracks_to_measures(track_list, user_config, test_defaults, test_cov_asymptote)
    individual_measures_dfs = individual_measures_to_dfs(tracks_by_groups, test_defaults, user_config)
    # calculate group averages of measures
    time_averages = time_average(individual_measures_dfs, test_defaults, user_config)
    group_measures_by_coverage = cov_measure_average(individual_measures_dfs, test_defaults, user_config, 'coverage')
    group_measures_by_pica = cov_measure_average(individual_measures_dfs, test_defaults, user_config, 'pica')
    group_measures_by_pgca = cov_measure_average(individual_measures_dfs, test_defaults, user_config, 'pgca')
    group_measures_by_percent_coverage = percent_coverage_average(individual_measures_dfs, test_defaults, user_config)
    # set up model fit defaults
    model_params = set_up_fits()
    # fit initial models on individual track data
    fits = fit_all(individual_measures_dfs, test_defaults, model_params)
    # change bounds based on the distribution of the parameters
    fit_upper_bounds, fit_lower_bounds, fit_initial_params = find_fit_bounds(fits, user_config)
    # refit the models on individual track data
    bounded_fits = re_fit_all(individual_measures_dfs, test_defaults, model_params, fit_upper_bounds, fit_lower_bounds,
                              fit_initial_params)
    return fits, fit_lower_bounds, fit_initial_params, fit_upper_bounds, bounded_fits
