import os
from collections import defaultdict
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from opynfield.config.defaults_settings import Defaults
from opynfield.config.model_settings import ModelSpecification
from opynfield.config.plot_settings import PlotSettings
from opynfield.config.user_input import UserInput
from opynfield.calculate_measures.standard_track import StandardTrack
from itertools import chain, zip_longest


def generate_fig_title(path: str, i: int, x_measure: str, y_measure: str, model_fit: bool, extension: str):
    path = path + f'individual_{i}_{x_measure}_vs_{y_measure}'
    if model_fit:
        path = path + '_with_model'
    path = path + extension
    return path


def plot_time_measure(group: str, i: int, measure: str, measure_data: pd.DataFrame, model_params: pd.DataFrame,
                      model_info: ModelSpecification, plot_settings: PlotSettings, user_config: UserInput):
    # create figure and axes objects for the plot
    fig, ax = plt.subplots()
    # define the x and y to be plotted
    # y is the measure for the individual
    y_plot = measure_data.iloc[i][1:].values
    # x is time in seconds
    x_plot = np.arange(len(y_plot))
    # scatter plot
    ax.scatter(x_plot, y_plot, s=plot_settings.marker_size, c=plot_settings.marker_color)
    if plot_settings.individual_model_fit:
        # plot the model fit
        fit_params = model_params.iloc[i].values
        if ~np.isnan(fit_params[0]):  # if the fit was successful
            y_fit = model_info.model.model_function(x_plot, *fit_params)
            ax.plot(x_plot, y_fit, c=plot_settings.fit_color, alpha=plot_settings.alpha)
            if plot_settings.equation:
                equation_str = generate_individual_equation_str(fit_params, model_info.model.display_parts)
                ax.set_title(f'model fit: {equation_str}')
    # add the axis labels
    ax.set_xlabel('time (s)')
    ax.set_ylabel(f'{measure}')
    # add the plot title
    fig.suptitle(f'{measure} by time individual {i} from group {group}')
    # set axis limits
    if measure not in ['activity', 'percent_coverage', 'pica', 'pgca', 'coverage']:
        # ax.set_xlim()
        ax.set_ylim((-0.1, 1.1))
    if plot_settings.display_individual_figures:
        # show the figure
        fig.show()
    if plot_settings.save_individual_figures:
        # save the figure
        path = user_config.result_path + '/Individuals/' + user_config.groups_to_paths[group] + '/Plots/by_time/'
        os.makedirs(path, exist_ok=True)
        fig_path = generate_fig_title(path, i, 'time', measure, plot_settings.individual_model_fit,
                                      plot_settings.fig_extension)
        fig.savefig(fname=fig_path, bbox_inches='tight')
    plt.close(fig=fig)
    return


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def generate_individual_equation_str(params, display_parts):
    equation_parts = list(display_parts)
    string_params = [str(truncate(x, 4)) for x in params]
    parts = [x for x in chain(*zip_longest(equation_parts, string_params)) if x is not None]
    display_equation = ''.join(parts)
    return display_equation


def plot_cmeasure_measure(x_measure: str, group: str, i: int, measure: str, measure_data_x: pd.DataFrame,
                          measure_data_y: pd.DataFrame, model_params: pd.DataFrame, model_info: ModelSpecification,
                          plot_settings: PlotSettings, user_config: UserInput):
    # create figure and axes objects for the plot
    fig, ax = plt.subplots()
    # define the x and y to be plotted
    # y is the measure for the individual
    y_plot = measure_data_x.iloc[i][1:].values
    # x is the coverage measure for the individual
    x_plot = measure_data_y.iloc[i][1:].values
    # scatter plot
    ax.scatter(x_plot, y_plot, s=plot_settings.marker_size, c=plot_settings.marker_color)
    if plot_settings.individual_model_fit:
        # plot the model fit
        fit_params = model_params.iloc[i].values
        if ~np.isnan(fit_params[0]):  # if the fit was successful
            y_fit = model_info.model.model_function(x_plot.astype(float), *fit_params)
            ax.plot(x_plot, y_fit, c=plot_settings.fit_color, alpha=plot_settings.alpha)
            if plot_settings.equation:
                equation_str = generate_individual_equation_str(fit_params, model_info.model.display_parts)
                ax.set_title(f'model fit: {equation_str}')
    # add the axis labels
    ax.set_xlabel(f'{x_measure}')
    ax.set_ylabel(f'{measure}')
    # add the plot title
    fig.suptitle(f'{measure} by {x_measure} individual {i} from group {group}')
    # set axis limits
    if measure != 'activity':
        # ax.set_xlim()
        ax.set_ylim((-0.1, 1.1))
    if plot_settings.display_individual_figures:
        # show the figure
        fig.show()
    if plot_settings.save_individual_figures:
        # save the figure
        path = user_config.result_path + '/Individuals/' + user_config.groups_to_paths[group] + '/Plots/by_' \
               + x_measure + '/'
        os.makedirs(path, exist_ok=True)
        fig_path = generate_fig_title(path, i, x_measure, measure, plot_settings.individual_model_fit,
                                      plot_settings.fig_extension)
        fig.savefig(fname=fig_path, bbox_inches='tight')
    plt.close(fig=fig)
    return


def plot_all_individuals_by_time(group: str, group_measures: dict[str, pd.DataFrame],
                                 group_model_params: dict[str, pd.DataFrame],
                                 model_info: dict[str, ModelSpecification], defaults: Defaults,
                                 plot_settings: PlotSettings, user_config: UserInput):
    for measure in defaults.time_averaged_measures:
        if measure != 'r':
            for i in range(group_measures[measure].shape[0]):
                plot_time_measure(group, i, measure, group_measures[measure],
                                  group_model_params[measure].reset_index().drop(columns='index'), model_info[measure],
                                  plot_settings, user_config)
    return


def plot_all_individuals_by_cmeasure(x_measure: str, group: str, group_measures: dict[str, pd.DataFrame],
                                     group_model_params: dict[str, pd.DataFrame],
                                     model_info: dict[str, ModelSpecification], defaults: Defaults,
                                     plot_settings: PlotSettings, user_config: UserInput):
    for measure in defaults.coverage_averaged_measures:
        for i in range(group_measures[measure].shape[0]):
            plot_cmeasure_measure(x_measure, group, i, measure, group_measures[measure], group_measures[x_measure],
                                  group_model_params[measure].reset_index().drop(columns='index'), model_info[measure],
                                  plot_settings, user_config)

    pass


def plot_all_individuals(measures: dict[str, dict[str, pd.DataFrame]],
                         model_params: dict[str, dict[str, dict[str, pd.DataFrame]]],
                         model_info: dict[str, dict[str, ModelSpecification]], defaults: Defaults,
                         plot_settings: PlotSettings, user_config: UserInput):
    for group in measures:
        # plot all individuals by time
        print(f'Plotting Individuals From Group {group} by time')
        plot_all_individuals_by_time(group, measures[group], model_params[group]['time'], model_info['time'], defaults,
                                     plot_settings, user_config)
        # plot all individuals by coverage measure
        for x_measure in ['coverage', 'pica', 'pgca', 'percent_coverage']:
            print(f'Plotting Individuals From Group {group} by {x_measure}')
            plot_all_individuals_by_cmeasure(x_measure, group, measures[group], model_params[group][x_measure],
                                             model_info[x_measure], defaults, plot_settings, user_config)
    return


def plot_individual_trace(track: StandardTrack, i: int, group: str, plot_settings: PlotSettings, user_input: UserInput):
    # create figure and axes objects for the plot
    fig, ax = plt.subplots()
    # define the x and y to be plotted
    x_starts = track.x[:-1]
    y_starts = track.y[:-1]
    x_stops = track.x[1:]
    y_stops = track.y[1:]
    t_scaled = np.arange(len(track.x))
    cmap = matplotlib.cm.get_cmap(plot_settings.colormap_name)
    # plot each step segment and color it by the time
    for j in range(len(x_starts)):
        ax.plot([x_starts[j], x_stops[j]], [y_starts[j], y_stops[j]], c=cmap(t_scaled[j]), alpha=plot_settings.alpha)
    # plot the arena
    angle = np.linspace(0, 2 * np.pi, 150)
    x = user_input.arena_radius_cm * np.cos(angle)
    y = user_input.arena_radius_cm * np.sin(angle)
    ax.plot(x, y, c=plot_settings.edge_color)
    ax.set_xlabel('X Coordinate (cm)')
    ax.set_ylabel('Y Coordinate (cm)')
    fig.suptitle(f'Individual {i} From Group {group} Track Trace')
    norm = matplotlib.colors.Normalize(vmin=t_scaled[0], vmax=t_scaled[-1])
    fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap))
    if plot_settings.display_individual_figures:
        # show the figure
        fig.show()
    if plot_settings.save_individual_figures:
        # save the figure
        path = user_input.result_path + '/Individuals/' + user_input.groups_to_paths[group] + '/Plots/traces/'
        os.makedirs(path, exist_ok=True)
        fig_path = path + 'individual_' + str(i) + plot_settings.fig_extension
        fig.savefig(fname=fig_path, bbox_inches='tight')
    plt.close(fig=fig)
    return


def plot_traces(tracks_by_groups: defaultdict[str: list[StandardTrack]], plot_settings: PlotSettings,
                user_input: UserInput):
    for group in tracks_by_groups:
        for i, track in enumerate(tracks_by_groups[group]):
            plot_individual_trace(track, i, group, plot_settings, user_input)
    return
