import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.opynfield.config.model_settings import ModelSpecification
from src.opynfield.config.defaults_settings import Defaults
from src.opynfield.config.plot_settings import PlotSettings
from src.opynfield.config.user_input import UserInput


def generate_fig_title(path: str, x_measure: str, y_measure: str, model_fit: bool, error: bool, extension: str):
    path = path + f'{x_measure}_vs_{y_measure}'
    if model_fit:
        path = path + '_with_model'
    if model_fit and error:
        path = path + '_and'
    if error:
        path = path + '_with_error'
    path = path + extension
    return path


def plot_time_comparison(x_measure: str, y_measure: str, time_averages: dict[str, dict[str, pd.DataFrame]],
                         fits: dict[str, dict[str, dict[str, pd.DataFrame]]], specs: ModelSpecification,
                         plot_settings: PlotSettings, user_inputs: UserInput):
    # time_averages -> group -> y_measure -> df with averages and sems
    # fits -> group -> x_measure -> y_measure -> df with parameters

    # create figure and axes objects for the plot
    fig, ax = plt.subplots()

    # loop through groups for each step so no layers work out right

    # first do error bars if needed
    if plot_settings.group_error_bars:
        for group in time_averages:
            # define that group's x and y values
            y_plot = time_averages[group][y_measure].iloc[0][2:]
            y_error = time_averages[group][y_measure].iloc[1][2:]
            x_plot = np.arange(len(y_plot))
            ax.errorbar(x_plot, y_plot, yerr=y_error, xerr=None, fmt='none', ecolor=plot_settings.group_colors[group],
                        errorevery=plot_settings.n_between_error, elinewidth=plot_settings.error_width,
                        alpha=plot_settings.alpha)
    # then do the scatter plots for all groups:
    for group in time_averages:
        y_plot = time_averages[group][y_measure].iloc[0][2:]
        x_plot = np.arange(len(y_plot))
        ax.scatter(x_plot, y_plot, s=plot_settings.marker_size, c=plot_settings.group_colors[group])

    # then do the model fits if needed:
    if plot_settings.group_model_fit:
        for group in time_averages:
            y_plot = time_averages[group][y_measure].iloc[0][2:]
            x_plot = np.arange(len(y_plot))
            params = fits[group][x_measure][y_measure].values
            y_fit = specs.model.model_function(x_plot, *params)
            ax.plot(x_plot, y_fit, c=plot_settings.group_colors[group], alpha=plot_settings.alpha)

    # add the axis labels
    ax.set_xlabel('time (s)')
    ax.set_ylabel(f'{y_measure}')

    # add the plot title
    fig.suptitle(f'{y_measure} by time')

    # set axis limits
    if y_measure not in ['activity', 'percent_coverage', 'pica', 'pgca', 'coverage']:
        # ax.set_xlim()
        ax.set_ylim((-0.1, 1.1))

    if plot_settings.display_solo_group_figures:
        # show the figure
        fig.show()

    if plot_settings.save_group__comparison_figures:
        # save the figure
        path = user_inputs.result_path + '/GroupComparisonPlots/by_time/'
        os.makedirs(path, exist_ok=True)
        fig_path = generate_fig_title(path, 'time', y_measure, plot_settings.group_model_fit,
                                      plot_settings.group_error_bars, plot_settings.fig_extension)
        fig.savefig(fname=fig_path, bbox_inches='tight')
    plt.close(fig=fig)
    return


def plot_cmeasure_comparison(x_measure: str, y_measure: str, cmeasure_averages: dict[str, pd.DataFrame],
                             group_fits: dict[str, dict[str, dict[str, pd.DataFrame]]], specs: ModelSpecification,
                             plot_settings: PlotSettings, user_input: UserInput):
    # time_averages -> group -> df with averages and sems by name
    # fits -> group -> x_measure -> y_measure -> df with parameters

    return


def plot_all_group_comparisons(group_averages: dict[str, dict],
                               group_fits: dict[str, dict[str, dict[str, pd.DataFrame]]],
                               model_params: dict[str, dict[str, ModelSpecification]], test_defaults: Defaults,
                               plot_settings: PlotSettings, user_config: UserInput):
    # do time plots
    print('Plotting Group Comparisons by time')
    for y_measure in test_defaults.time_averaged_measures:
        if y_measure != 'r':
            plot_time_comparison('time', y_measure, group_averages['time'], group_fits,
                                 model_params['time'][y_measure], plot_settings, user_config)

    # do cmeasure plots
    for x_measure in ['coverage', 'pica', 'pgca', 'percent_coverage']:
        print(f'Plotting Group Comparisons by {x_measure}')
        for y_measure in test_defaults.coverage_averaged_measures:
            # plot_cmeasure_comparison()
            plot_cmeasure_comparison(x_measure, y_measure, group_averages[x_measure], group_fits,
                                     model_params[x_measure][y_measure], plot_settings, user_config)
    return
