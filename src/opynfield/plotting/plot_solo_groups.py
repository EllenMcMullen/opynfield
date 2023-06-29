import pandas as pd
from opynfield.config.model_settings import ModelSpecification
from opynfield.config.defaults_settings import Defaults
from opynfield.config.plot_settings import PlotSettings
from opynfield.config.user_input import UserInput
import matplotlib.pyplot as plt
import numpy as np
from itertools import chain, zip_longest
import os


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def generate_group_equation_str(fit_params, display_parts):
    equation_parts = list(display_parts)
    string_params = [str(truncate(x, 4)) for x in fit_params]
    parts = [x for x in chain(*zip_longest(equation_parts, string_params)) if x is not None]
    display_equation = ''.join(parts)
    return display_equation


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


def plot_solo_group_measure_by_time(measure_by_time: pd.DataFrame, plot_settings: PlotSettings,
                                    model_specs: ModelSpecification, group_fits: pd.DataFrame, measure: str,
                                    group: str, user_config: UserInput):
    # create figure and axes objects for the plot
    fig, ax = plt.subplots()
    # define the x and y to be plotted
    # y is the measure for the group
    y_plot = measure_by_time.iloc[0][2:]
    # also have the error on that measure
    y_error = measure_by_time.iloc[1][2:]
    # x is time in sec
    x_plot = np.arange(len(y_plot))
    # do error first so that the markers will go on top of them
    if plot_settings.group_error_bars:
        ax.errorbar(x_plot, y_plot, yerr=y_error, xerr=None, fmt='none', ecolor=plot_settings.error_color,
                    errorevery=plot_settings.n_between_error, elinewidth=plot_settings.error_width,
                    alpha=plot_settings.alpha)
    # scatter plot
    ax.scatter(x_plot, y_plot, s=plot_settings.marker_size, c=plot_settings.marker_color)

    if plot_settings.group_model_fit:
        y_fit = model_specs.model.model_function(x_plot, *group_fits.values)
        ax.plot(x_plot, y_fit, c=plot_settings.fit_color, alpha=plot_settings.alpha)
        if plot_settings.equation:
            equation_str = generate_group_equation_str(group_fits.values.flatten().tolist(),
                                                       model_specs.model.display_parts)
            ax.set_title(f'model fit: {equation_str}')
    # add the axis labels
    ax.set_xlabel('time (s)')
    ax.set_ylabel(f'{measure}')
    # add the plot title
    fig.suptitle(f'{measure} by time group {group}')
    # set axis limits
    if measure not in ['activity', 'percent_coverage', 'pica', 'pgca', 'coverage']:
        # ax.set_xlim()
        ax.set_ylim((-0.1, 1.1))
    if plot_settings.display_solo_group_figures:
        # show the figure
        fig.show()
    if plot_settings.save_solo_group_figures:
        # save the figure
        path = user_config.result_path + '/Groups/' + user_config.groups_to_paths[group] + '/Plots/by_time/'
        os.makedirs(path, exist_ok=True)
        fig_path = generate_fig_title(path, 'time', measure, plot_settings.group_model_fit,
                                      plot_settings.group_error_bars, plot_settings.fig_extension)
        fig.savefig(fname=fig_path, bbox_inches='tight')
    plt.close(fig=fig)
    return


def plot_solo_group_by_time(by_time: dict[str, pd.DataFrame], defaults: Defaults, plot_settings: PlotSettings,
                            model_params: dict[str, ModelSpecification], group_fits: dict[str, pd.DataFrame],
                            group: str, user_config: UserInput):
    for measure in defaults.time_averaged_measures:
        if measure != 'r':
            plot_solo_group_measure_by_time(by_time[measure].reset_index().drop(columns='index'), plot_settings,
                                            model_params[measure], group_fits[measure], measure, group, user_config)
    return


def plot_solo_group_by_cmeasure(by_coverage: pd.DataFrame, defaults: Defaults, cmeasure: str,
                                plot_settings: PlotSettings, model_params: dict[str, ModelSpecification],
                                group_fits: dict[str, pd.DataFrame], group: str, user_config: UserInput):
    for measure in defaults.coverage_averaged_measures:
        # create figure and axes objects for the plot
        fig, ax = plt.subplots()
        # define the x and y to be plotted
        # y is the measure for the group
        y_plot = by_coverage[f'{measure} mean'].values
        # also have the error on that measure
        y_error = by_coverage[f'{measure} sem'].values
        # x is the coverage measure for the group
        x_plot = by_coverage[f'{cmeasure} mean'].values
        # also have the error on the cmeasure
        x_error = by_coverage[f'{cmeasure} sem'].values
        # do error first so that the markers will go on top of them
        if plot_settings.group_error_bars:
            ax.errorbar(x_plot, y_plot, yerr=y_error, xerr=x_error, fmt='none', ecolor=plot_settings.error_color,
                        errorevery=plot_settings.n_between_error, elinewidth=plot_settings.error_width,
                        alpha=plot_settings.alpha)
        # scatter plot
        ax.scatter(x_plot, y_plot, s=plot_settings.marker_size, c=plot_settings.marker_color)
        if plot_settings.group_model_fit:
            model_specs = model_params[measure]
            measure_fits = group_fits[measure]
            y_fit = model_specs.model.model_function(x_plot, *measure_fits.values)
            ax.plot(x_plot, y_fit, c=plot_settings.fit_color, alpha=plot_settings.alpha)
            if plot_settings.equation:
                equation_str = generate_group_equation_str(measure_fits.values.flatten().tolist(),
                                                           model_specs.model.display_parts)
                ax.set_title(f'model fit: {equation_str}')
        # add the axis labels
        ax.set_xlabel(f'{cmeasure}')
        ax.set_ylabel(f'{measure}')
        # add the plot title
        fig.suptitle(f'{measure} by {cmeasure} group {group}')
        # set axis limits
        if measure != 'activity':
            # ax.set_xlim()
            ax.set_ylim((-0.1, 1.1))
        if plot_settings.display_solo_group_figures:
            # show the figure
            fig.show()
        if plot_settings.save_solo_group_figures:
            # save the figure
            path = user_config.result_path + '/Groups/' + user_config.groups_to_paths[group] + '/Plots/by_' + cmeasure \
                   + '/'
            os.makedirs(path, exist_ok=True)
            fig_path = generate_fig_title(path, cmeasure, measure, plot_settings.group_model_fit,
                                          plot_settings.group_error_bars, plot_settings.fig_extension)
            fig.savefig(fname=fig_path, bbox_inches='tight')
        plt.close(fig=fig)
    return


def plot_all_solo_groups(group_averages: dict[str, dict], group_fits: dict[str, dict[str, dict[str, pd.DataFrame]]],
                         model_params: dict[str, dict[str, ModelSpecification]], test_defaults: Defaults,
                         plot_settings: PlotSettings, user_config: UserInput):
    for group in group_averages['time']:
        print(f'Plotting Group {group} by time')
        plot_solo_group_by_time(group_averages['time'][group], test_defaults, plot_settings, model_params['time'],
                                group_fits[group]['time'], group, user_config)
        for x_measure in ['coverage', 'pica', 'pgca', 'percent_coverage']:
            print(f'Plotting Group {group} by {x_measure}')
            plot_solo_group_by_cmeasure(group_averages[x_measure][group], test_defaults, x_measure, plot_settings,
                                        model_params[x_measure], group_fits[group][x_measure], group, user_config)
    return
