import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from opynfield.config.model_settings import ModelSpecification
from opynfield.config.defaults_settings import Defaults
from opynfield.config.plot_settings import PlotSettings
from opynfield.config.user_input import UserInput


def generate_fig_title(
    path: str,
    x_measure: str,
    y_measure: str,
    model_fit: bool,
    error: bool,
    extension: str,
) -> str:
    """This function generates a figure title to save the figure in from the component parts

    :param path: path to the plot folder
    :type path: str
    :param x_measure: the x-axis of the plot
    :type x_measure: str
    :param y_measure: the y-axis of the plot
    :type y_measure: str
    :param model_fit: whether the plot includes a model fit
    :type model_fit: bool
    :param error: whether the plot includes error bars
    :type error: bool
    :param extension: what file extension / format to save the plot in
    :type extension: str
    :return: the path to save the plot in
    :rtype: str
    """
    path = path + f"{x_measure}_vs_{y_measure}"
    if model_fit:
        path = path + "_with_model"
    if model_fit and error:
        path = path + "_and"
    if error:
        path = path + "_with_error"
    path = path + extension
    return path


def plot_time_comparison(
    x_measure: str,
    y_measure: str,
    time_averages: dict[str, dict[str, pd.DataFrame]],
    fits: dict[str, dict[str, dict[str, pd.DataFrame]]],
    specs: ModelSpecification,
    plot_settings: PlotSettings,
    user_inputs: UserInput,
):
    """This function plots all the group averages against each other for a time vs y-measure relationship

    :param x_measure: the x-measure (time)
    :type x_measure: str
    :param y_measure: the y-measure
    :type y_measure: str
    :param time_averages: the averages to use to plot, indexed by group and y-measure
    :type time_averages: dict[str, dict[str, pd.DataFrame]]
    :param fits: the model parameters to use, indexed by group and y-measure
    :type fits: dict[str, dict[str, dict[str, pd.DataFrame]]]
    :param specs: the model settings to use
    :type specs: ModelSpecification
    :param plot_settings: the plot settings to use
    :type plot_settings: PlotSettings
    :param user_inputs: the user inputs to use
    :type user_inputs: UserInput
    """
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
            ax.errorbar(
                x_plot,
                y_plot,
                yerr=y_error,
                xerr=None,
                fmt="none",
                ecolor=plot_settings.group_colors[group],
                errorevery=plot_settings.n_between_error,
                elinewidth=plot_settings.error_width,
                alpha=plot_settings.alpha,
            )
    # then do the scatter plots for all groups:
    for group in time_averages:
        y_plot = time_averages[group][y_measure].iloc[0][2:]
        x_plot = np.arange(len(y_plot))
        ax.scatter(
            x_plot,
            y_plot,
            s=plot_settings.marker_size,
            c=plot_settings.group_colors[group],
            label=group,
        )

    # then do the model fits if needed:
    if plot_settings.group_model_fit:
        for group in time_averages:
            y_plot = time_averages[group][y_measure].iloc[0][2:]
            x_plot = np.arange(len(y_plot))
            params = fits[group][x_measure][y_measure].values
            y_fit = specs.model.model_function(x_plot, *params)
            ax.plot(
                x_plot,
                y_fit,
                c=plot_settings.group_colors[group],
                alpha=plot_settings.alpha,
            )

    # add the axis labels
    ax.set_xlabel("time (s)")
    ax.set_ylabel(f"{y_measure}")

    # add the plot title
    fig.suptitle(f"{y_measure} by time")

    # add the legend of groups
    ax.legend()

    # set axis limits
    if y_measure not in ["activity", "percent_coverage", "pica", "pgca", "coverage"]:
        # ax.set_xlim()
        ax.set_ylim((-0.1, 1.1))

    if plot_settings.display_solo_group_figures:
        # show the figure
        fig.show()

    if plot_settings.save_group__comparison_figures:
        # save the figure
        path = user_inputs.result_path + "/GroupComparisonPlots/by_time/"
        os.makedirs(path, exist_ok=True)
        fig_path = generate_fig_title(
            path,
            "time",
            y_measure,
            plot_settings.group_model_fit,
            plot_settings.group_error_bars,
            plot_settings.fig_extension,
        )
        fig.savefig(fname=fig_path, bbox_inches="tight")
    plt.close(fig=fig)
    return


def plot_cmeasure_comparison(
    x_measure: str,
    y_measure: str,
    cmeasure_averages: dict[str, pd.DataFrame],
    group_fits: dict[str, dict[str, dict[str, pd.DataFrame]]],
    specs: ModelSpecification,
    plot_settings: PlotSettings,
    user_input: UserInput,
):
    """This function plots all the group averages against each other for a coverage-measure vs y-measure relationship

    :param x_measure: the coverage-measure
    :type x_measure: str
    :param y_measure: the y-measure
    :type y_measure: str
    :param cmeasure_averages: the averages to use to plot, indexed by group and y-measure
    :type cmeasure_averages: dict[str, dict[str, pd.DataFrame]]
    :param group_fits: the model parameters to use, indexed by group and y-measure
    :type group_fits: dict[str, dict[str, dict[str, pd.DataFrame]]]
    :param specs: the model settings to use
    :type specs: ModelSpecification
    :param plot_settings: the plot settings to use
    :type plot_settings: PlotSettings
    :param user_input: the user inputs to use
    :type user_input: UserInput
    """
    # cmeasure_averages -> group -> df with averages and sems by name
    # fits -> group -> x_measure -> y_measure -> df with parameters

    # create figure and axes objects for the plot
    fig, ax = plt.subplots()

    # loop through groups for each step so no layers work out right
    # first do error bars if needed
    if plot_settings.group_error_bars:
        for group in cmeasure_averages:
            # define that group's x and y values
            y_plot = cmeasure_averages[group][f"{y_measure} mean"]
            y_error = cmeasure_averages[group][f"{y_measure} sem"]
            x_plot = cmeasure_averages[group][f"{x_measure} mean"]
            x_error = cmeasure_averages[group][f"{x_measure} sem"]
            ax.errorbar(
                x_plot,
                y_plot,
                yerr=y_error,
                xerr=x_error,
                fmt="none",
                ecolor=plot_settings.group_colors[group],
                errorevery=plot_settings.n_between_error,
                elinewidth=plot_settings.error_width,
                alpha=plot_settings.alpha,
            )
    # then do the scatter plots for all groups:
    for group in cmeasure_averages:
        y_plot = cmeasure_averages[group][f"{y_measure} mean"]
        x_plot = cmeasure_averages[group][f"{x_measure} mean"]
        ax.scatter(
            x_plot,
            y_plot,
            s=plot_settings.marker_size,
            c=plot_settings.group_colors[group],
            label=group,
        )

    # then do the model fits if needed:
    if plot_settings.group_model_fit:
        for group in cmeasure_averages:
            x_plot = cmeasure_averages[group][f"{x_measure} mean"]
            params = group_fits[group][x_measure][y_measure].values
            y_fit = specs.model.model_function(x_plot, *params)
            ax.plot(
                x_plot,
                y_fit,
                c=plot_settings.group_colors[group],
                alpha=plot_settings.alpha,
            )

    # add the axis labels
    ax.set_xlabel(f"f{x_measure}")
    ax.set_ylabel(f"{y_measure}")

    # add the plot title
    fig.suptitle(f"{y_measure} by {x_measure}")

    # add the legend of groups
    ax.legend()

    # set axis limits
    if y_measure != "activity":
        # ax.set_xlim()
        ax.set_ylim((-0.1, 1.1))

    if plot_settings.display_solo_group_figures:
        # show the figure
        fig.show()

    if plot_settings.save_group__comparison_figures:
        # save the figure
        path = user_input.result_path + "/GroupComparisonPlots/by_" + x_measure + "/"
        os.makedirs(path, exist_ok=True)
        fig_path = generate_fig_title(
            path,
            x_measure,
            y_measure,
            plot_settings.group_model_fit,
            plot_settings.group_error_bars,
            plot_settings.fig_extension,
        )
        fig.savefig(fname=fig_path, bbox_inches="tight")
    plt.close(fig=fig)
    return


def plot_all_group_comparisons(
    group_averages: dict[str, dict],
    group_fits: dict[str, dict[str, dict[str, pd.DataFrame]]],
    model_params: dict[str, dict[str, ModelSpecification]],
    test_defaults: Defaults,
    plot_settings: PlotSettings,
    user_config: UserInput,
):
    """This function coordinates the plotting of all the x-measure (both time and coverage-measure) vs y-measure relationships

    :param group_averages: the group average data to use, indexed by group and then x measure
    :type group_averages: dict[str, dict]
    :param group_fits: the model parameter fits to use, indexed by group, x-measure, and y-measure
    :type group_fits: dict[str, dict[str, dict[str, pd.DataFrame]]]
    :param model_params: the model settings to use, indexed by x measure and y measure
    :type model_params: dict[str, dict[str, ModelSpecification]]
    :param test_defaults: the default settings to use
    :type test_defaults: Defaults
    :param plot_settings: the plot settings to use
    :type plot_settings: PlotSettings
    :param user_config: the user inputs to use
    :type user_config: UserInput
    """
    # do time plots
    print("Plotting Group Comparisons by time")
    for y_measure in test_defaults.time_averaged_measures:
        if y_measure != "r":
            plot_time_comparison(
                "time",
                y_measure,
                group_averages["time"],
                group_fits,
                model_params["time"][y_measure],
                plot_settings,
                user_config,
            )

    # do cmeasure plots
    for x_measure in ["coverage", "pica", "pgca", "percent_coverage"]:
        print(f"Plotting Group Comparisons by {x_measure}")
        for y_measure in test_defaults.coverage_averaged_measures:
            # plot_cmeasure_comparison()
            plot_cmeasure_comparison(
                x_measure,
                y_measure,
                group_averages[x_measure],
                group_fits,
                model_params[x_measure][y_measure],
                plot_settings,
                user_config,
            )
    return
