from opynfield.config.user_input import UserInput
from opynfield.readin.run_all import run_all_track_types
from opynfield.readin.summary_file import summary_file
from opynfield.config.defaults_settings import Defaults
from opynfield.config.cov_asymptote import CoverageAsymptote
from opynfield.calculate_measures.calculate_measures import tracks_to_measures
from opynfield.summarize_measures.summarize_individuals import individual_measures_to_dfs
from opynfield.summarize_measures.summarize_groups import all_group_averages
from opynfield.config.model_settings import set_up_fits
from opynfield.fit_models.fit_individual_models import (
    fit_all,
    find_fit_bounds,
    re_fit_all,
)
from opynfield.fit_models.fit_group_models import group_fit_all
from opynfield.stat_test.stat_test import format_params, format_group_params, run_tests
from copy import deepcopy
from opynfield.plotting.plot_individuals import plot_all_individuals, plot_traces
from opynfield.config.plot_settings import PlotSettings
from opynfield.plotting.plot_solo_groups import plot_all_solo_groups
from opynfield.plotting.plot_solo_groups_with_individuals import (
    plot_components_of_solo_groups,
)
from opynfield.plotting.plot_group_comparisons import plot_all_group_comparisons
import os

curr_dir = os.chdir(os.getcwd())
path_dir = curr_dir + '/TestRunResults2'


def run():
    """This function coordinates running a full analysis on test data"""
    # create your user config settings
    user_config = UserInput(
        {"Canton S": ["Buridian Tracker"], "Canton S 2": ["Buridian Tracker"]},
        {"Canton S": "CS1", "Canton S 2": "CS2"},
        4.2,
        30,
        1,
        1,
        0.001,
        True,
        path_dir,
    )
    user_config.prep_directory()
    # read in the data
    track_list = run_all_track_types(
        user_config.groups_and_types,
        user_config.verbose,
        user_config.arena_radius_cm,
        user_config.running_window_length,
        user_config.window_step_size,
        user_config.sample_freq,
        user_config.time_bin_size,
        user_config.trim,
    )
    # set the default parameters (or override)
    test_defaults = Defaults()
    # identify functional form for PICA and PGCA (or override)
    test_cov_asymptote = CoverageAsymptote()
    # calculate measures from track data
    standard_tracks, tracks_by_groups = tracks_to_measures(
        track_list, user_config, test_defaults, test_cov_asymptote
    )
    individual_measures_dfs = individual_measures_to_dfs(
        tracks_by_groups, test_defaults, user_config
    )
    # calculate group averages of measures
    group_averages = all_group_averages(
        individual_measures_dfs, test_defaults, user_config
    )
    # set up model fit defaults
    model_params = set_up_fits()
    # fit initial models on individual track data
    fits = fit_all(individual_measures_dfs, test_defaults, model_params)
    # change bounds based on the distribution of the parameters
    fit_upper_bounds, fit_lower_bounds, fit_initial_params = find_fit_bounds(
        fits, user_config
    )
    # refit the models on individual track data with the bounds
    bounded_fits = re_fit_all(
        individual_measures_dfs,
        test_defaults,
        model_params,
        fit_upper_bounds,
        fit_lower_bounds,
        fit_initial_params,
    )
    # fit group models with the bounds
    group_fits = group_fit_all(
        individual_measures_dfs,
        test_defaults,
        model_params,
        fit_upper_bounds,
        fit_lower_bounds,
        fit_initial_params,
    )
    # format the bounded_fits to do statistical tests
    formatted_bounded_fits = format_params(
        deepcopy(bounded_fits), test_defaults, user_config
    )
    # format the group fits to save out
    format_group_params(deepcopy(group_fits), test_defaults, user_config)
    # run the stat tests with the model fits
    run_tests(formatted_bounded_fits, test_defaults, user_config)
    # plot individuals with model fits
    plot_settings = PlotSettings(group_colors={"Canton S": "b", "Canton S 2": "r"})
    # create a track summary document
    summary_file(
        tracks_by_groups,
        test_cov_asymptote,
        test_defaults,
        model_params,
        plot_settings,
        user_config,
    )
    # plot individuals with model fits
    plot_all_individuals(
        individual_measures_dfs,
        bounded_fits,
        model_params,
        test_defaults,
        plot_settings,
        user_config,
    )
    # plot individual traces
    plot_traces(tracks_by_groups, plot_settings, user_config)
    # plot groups with model fits and error bars
    plot_all_solo_groups(
        group_averages,
        group_fits,
        model_params,
        test_defaults,
        plot_settings,
        user_config,
    )
    # plot individual makeup of groups with individual and group models and error bars
    plot_components_of_solo_groups(
        individual_measures_dfs,
        bounded_fits,
        group_averages,
        group_fits,
        model_params,
        test_defaults,
        plot_settings,
        user_config,
    )
    # plot group comparisons with models and error bars
    plot_all_group_comparisons(
        group_averages,
        group_fits,
        model_params,
        test_defaults,
        plot_settings,
        user_config,
    )
    # TODO: other csv input format
    # TODO: testing code
    # TODO: other summary info in stats folder separate file
    # TODO: check the assumptions of time plots and models based on the time binning
    # TODO: add verbose setting
    return
