import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from opynfield.config.model_settings import ModelSpecification
from opynfield.config.defaults_settings import Defaults
from opynfield.config.plot_settings import PlotSettings
from opynfield.config.user_input import UserInput


def generate_view_title(
    path: str,
    x_measure: str,
    y_measure: str,
    individual_models: bool,
    group_model: bool,
    group_error: bool,
    extension: str,
):
    path = path + f"{x_measure}_vs_{y_measure}"
    parts = list()
    if individual_models:
        parts.append("_with_individual_models")
    if group_model:
        parts.append("_with_group_model")
    if group_error:
        parts.append("_with_group_error")
    path = path + "_and".join(parts)
    path = path + extension
    return path


def plot_group_individual_comparison_cmeasure(
    group: str,
    x_measure: str,
    y_measure: str,
    individuals_x: pd.DataFrame,
    individuals_y: pd.DataFrame,
    individuals_params: pd.DataFrame,
    group_ys_df: pd.DataFrame,
    group_params: pd.DataFrame,
    model_spec: ModelSpecification,
    plot_settings: PlotSettings,
    user_inputs: UserInput,
):
    # create figure and axes objects for the plot
    fig, ax = plt.subplots()

    # first plot all the individuals
    for i in range(individuals_y.shape[0]):
        y_plot = individuals_y.iloc[i][1:].values
        x_plot = individuals_x.iloc[i][1:].values
        ax.scatter(
            x_plot,
            y_plot,
            s=plot_settings.marker_size,
            c=plot_settings.marker_color,
            alpha=0.1,
        )
        # plot their models if needed
        if plot_settings.individual_model_fit:
            params = individuals_params.iloc[i].values
            if ~np.isnan(params[0]):
                y_fit = model_spec.model.model_function(x_plot.astype(float), *params)
                ax.plot(x_plot, y_fit, c=plot_settings.marker_color, alpha=0.3)

    # plot the group error bars if needed (do first so that the points go on top)
    y_plot_group = group_ys_df[f"{y_measure} mean"].values
    y_err_group = group_ys_df[f"{y_measure} sem"].values
    x_plot_group = group_ys_df[f"{x_measure} mean"].values
    x_err_group = group_ys_df[f"{x_measure} sem"].values
    if plot_settings.group_error_bars:
        ax.errorbar(
            x_plot_group,
            y_plot_group,
            yerr=y_err_group,
            xerr=x_err_group,
            fmt="none",
            ecolor="k",
            errorevery=plot_settings.n_between_error,
            elinewidth=plot_settings.error_width,
            alpha=plot_settings.alpha,
        )
    # then plot the group averages
    ax.scatter(x_plot_group, y_plot_group, s=plot_settings.marker_size, c="k")
    # then plot their model if needed
    if plot_settings.group_model_fit:
        y_fit_group = model_spec.model.model_function(
            x_plot_group, *group_params.values
        )
        ax.plot(x_plot_group, y_fit_group, c="k", alpha=0.5)

    # set the axes labels
    ax.set_xlabel(f"{x_measure}")
    ax.set_ylabel(f"{y_measure}")
    # add the plot title
    fig.suptitle(f"{y_measure} by {x_measure} group {group}")
    # set axis limits
    if y_measure != "activity":
        # ax.set_xlim()
        ax.set_ylim((-0.1, 1.1))
    # show the figure
    if plot_settings.display_solo_group_figures:
        fig.show()
    # save the figure
    if plot_settings.save_combined_view_figures:
        path = (
            user_inputs.result_path
            + "/Groups/"
            + user_inputs.groups_to_paths[group]
            + "/Plots/individual_view_by_"
            + x_measure
            + "/"
        )
        os.makedirs(path, exist_ok=True)
        fig_path = generate_view_title(
            path,
            x_measure,
            y_measure,
            plot_settings.individual_model_fit,
            plot_settings.group_model_fit,
            plot_settings.group_error_bars,
            plot_settings.fig_extension,
        )
        fig.savefig(fname=fig_path, bbox_inches="tight")
    plt.close()
    return


def plot_group_individual_comparison_time(
    group: str,
    x_measure: str,
    y_measure: str,
    individuals_y: pd.DataFrame,
    individuals_params: pd.DataFrame,
    group_y: pd.DataFrame,
    group_params: pd.DataFrame,
    model_spec: ModelSpecification,
    plot_settings: PlotSettings,
    user_inputs: UserInput,
):
    # create figure and axes objects for the plot
    fig, ax = plt.subplots()

    # first plot all the individuals
    for i in range(individuals_y.shape[0]):
        y_plot = individuals_y.iloc[i][1:].values
        x_plot = np.arange(len(y_plot))
        ax.scatter(
            x_plot,
            y_plot,
            s=plot_settings.marker_size,
            c=plot_settings.marker_color,
            alpha=0.1,
        )
        # plot their models if needed
        if plot_settings.individual_model_fit:
            params = individuals_params.iloc[i]
            y_fit = model_spec.model.model_function(x_plot, *params)
            ax.plot(x_plot, y_fit, c=plot_settings.marker_color, alpha=0.3)

    # plot the group error bars if needed (do first so that the points go on top)
    y_plot_group = group_y.iloc[0][2:]
    y_err_group = group_y.iloc[1][2:]
    x_plot_group = np.arange(len(y_plot_group))
    if plot_settings.group_error_bars:
        ax.errorbar(
            x_plot_group,
            y_plot_group,
            yerr=y_err_group,
            xerr=None,
            fmt="none",
            ecolor="k",
            errorevery=plot_settings.n_between_error,
            elinewidth=plot_settings.error_width,
            alpha=plot_settings.alpha,
        )
    # then plot the group averages
    ax.scatter(x_plot_group, y_plot_group, s=plot_settings.marker_size, c="k")
    # then plot their model if needed
    if plot_settings.group_model_fit:
        y_fit_group = model_spec.model.model_function(
            x_plot_group, *group_params.values
        )
        ax.plot(x_plot_group, y_fit_group, c="k", alpha=0.5)

    # set the axes labels
    ax.set_xlabel("time (s)")
    ax.set_ylabel(f"{y_measure}")
    # add the plot title
    fig.suptitle(f"{y_measure} by {x_measure} group {group}")
    # set axis limits
    if y_measure not in ["activity", "percent_coverage", "pica", "pgca", "coverage"]:
        # ax.set_xlim()
        ax.set_ylim((-0.1, 1.1))
    # show the figure
    if plot_settings.display_solo_group_figures:
        fig.show()
    # save the figure
    if plot_settings.save_combined_view_figures:
        path = (
            user_inputs.result_path
            + "/Groups/"
            + user_inputs.groups_to_paths[group]
            + "/Plots/individual_view_by_"
            + x_measure
            + "/"
        )
        os.makedirs(path, exist_ok=True)
        fig_path = generate_view_title(
            path,
            x_measure,
            y_measure,
            plot_settings.individual_model_fit,
            plot_settings.group_model_fit,
            plot_settings.group_error_bars,
            plot_settings.fig_extension,
        )
        fig.savefig(fname=fig_path, bbox_inches="tight")
    plt.close()
    return


def plot_components_of_solo_groups(
    individuals: dict[str, dict[str, pd.DataFrame]],
    individual_fits: dict[str, dict[str, dict[str, pd.DataFrame]]],
    groups: dict[str, dict],
    group_fits: dict[str, dict[str, dict[str, pd.DataFrame]]],
    model_specs: dict[str, dict[str, ModelSpecification]],
    defaults: Defaults,
    plot_settings: PlotSettings,
    user_inputs: UserInput,
):
    # groups is x_measure -> group -> y_measure -> averages and sems for time
    # groups is x_measure -> group -> averages and sems by name for cmeasure
    # individuals is group -> measure -> df with rows are individuals and columns are 'time' points
    # group_fits is group -> x_measure -> y_measure -> model params
    # individual_fits is group -> x_measure -> y_measure -> df with rows are individuals and cols are model params
    # model specs are x_measure -> y_measure -> ModelSpecification
    for group in groups["time"]:
        print(f"Plotting Group And Individuals of {group} by time")
        for y_measure in groups["time"][group]:
            if y_measure != "r":
                # for that group, x, and y
                # plot group average against all the individuals in that group
                plot_group_individual_comparison_time(
                    group,
                    "time",
                    y_measure,
                    individuals[group][y_measure],
                    individual_fits[group]["time"][y_measure],
                    groups["time"][group][y_measure],
                    group_fits[group]["time"][y_measure],
                    model_specs["time"][y_measure],
                    plot_settings,
                    user_inputs,
                )
        for x_measure in ["coverage", "pica", "pgca", "percent_coverage"]:
            print(f"Plotting Group And Individuals of {group} by {x_measure}")
            for y_measure in defaults.coverage_averaged_measures:
                plot_group_individual_comparison_cmeasure(
                    group,
                    x_measure,
                    y_measure,
                    individuals[group][x_measure],
                    individuals[group][y_measure],
                    individual_fits[group][x_measure][y_measure],
                    groups[x_measure][group],
                    group_fits[group][x_measure][y_measure],
                    model_specs[x_measure][y_measure],
                    plot_settings,
                    user_inputs,
                )
    return
