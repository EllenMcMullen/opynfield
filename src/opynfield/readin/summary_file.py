import sys
from dataclasses import fields
from collections import defaultdict

from opynfield.calculate_measures.standard_track import StandardTrack
from opynfield.config.cov_asymptote import CoverageAsymptote
from opynfield.config.defaults_settings import Defaults
from opynfield.config.model_settings import ModelSpecification
from opynfield.config.plot_settings import PlotSettings
from opynfield.config.user_input import UserInput


def summarize(
    tracks_by_group: defaultdict[str, list[StandardTrack]],
    test_cov_asymptote: CoverageAsymptote,
    user_defaults: Defaults,
    model_settings: dict[str, dict[str, ModelSpecification]],
    plot_settings: PlotSettings,
    user_config: UserInput,
):
    """This function summarizes information about the kinds of tracks read in after the read-in process is complete. It
    generates a text file of information about the tracks and parameters used on them

    :param tracks_by_group: the tracks to summarize
    :type tracks_by_group: defaultdict[str, list[StandardTrack]]
    :param test_cov_asymptote: the coverage asymptote information that was used
    :type test_cov_asymptote: CoverageAsymptote
    :param user_defaults: the default settings that were used
    :type user_defaults: Defaults
    :param model_settings: the model settings that were used
    :type model_settings: dict[str, dict[str, ModelSpecification]]
    :param plot_settings: the plot settings that were used
    :type plot_settings: PlotSettings
    :param user_config: the user inputs that were used
    :type user_config: UserInput
    """
    print("Tracks Run")
    print("__________")
    print("\n")
    print("N Per Group")
    for key, value in tracks_by_group.items():
        print(f"{key}: {len(value)}")
    print("\n")
    print("\n")
    print("Run Parameters")
    print("______________")
    print("\n")
    print("Coverage Asymptote Settings:")
    for field in fields(test_cov_asymptote):
        value = getattr(test_cov_asymptote, field.name)
        print(f"{field.name}: {value}")
    print("\n")
    print("Default Settings:")
    for field in fields(user_defaults):
        if field.name not in ["time_averaged_measures", "coverage_averaged_measures"]:
            value = getattr(user_defaults, field.name)
            print(f"{field.name}: {value}")
    print("\n")
    print("Model Settings:")
    for x_measure in model_settings:
        for y_measure in model_settings[x_measure]:
            print(f"{model_settings[x_measure][y_measure].axes}:")
            m = model_settings[x_measure][y_measure].model
            for field in fields(m):
                value = getattr(m, field.name)
                print(f"{field.name}: {value}")
    print("\n")
    print("Plot Settings:")
    for field in fields(plot_settings):
        value = getattr(plot_settings, field.name)
        print(f"{field.name}: {value}")
    print("\n")
    print("User Input Settings:")
    for field in fields(user_config):
        value = getattr(user_config, field.name)
        print(f"{field.name}: {value}")
    return


def summary_file(
    tracks_by_group: defaultdict[str, list[StandardTrack]],
    test_cov_asymptote: CoverageAsymptote,
    user_defaults: Defaults,
    model_settings: dict[str, dict[str, ModelSpecification]],
    plot_settings: PlotSettings,
    user_config: UserInput,
):
    """This function calls the summary information function and creates the text file output

    :param tracks_by_group: the tracks to summarize
    :type tracks_by_group: defaultdict[str, list[StandardTrack]]
    :param test_cov_asymptote: the coverage asymptote information that was used
    :type test_cov_asymptote: CoverageAsymptote
    :param user_defaults: the default settings that were used
    :type user_defaults: Defaults
    :param model_settings: the model settings that were used
    :type model_settings: dict[str, dict[str, ModelSpecification]]
    :param plot_settings: the plot settings that were used
    :type plot_settings: PlotSettings
    :param user_config: the user inputs that were used
    :type user_config: UserInput
    """
    print("Formatting Summary File")
    # set up the output file
    summary_file_path = user_config.result_path + "/summary.txt"
    orig_stdout = sys.stdout
    f = open(summary_file_path, "a")
    sys.stdout = f

    # do the summary stuff with print statements
    summarize(
        tracks_by_group,
        test_cov_asymptote,
        user_defaults,
        model_settings,
        plot_settings,
        user_config,
    )

    # close out the output file
    sys.stdout = orig_stdout
    f.close()
    return
