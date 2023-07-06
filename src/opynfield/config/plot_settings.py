from dataclasses import dataclass


@dataclass
class PlotSettings:
    """This dataclass defines many settings that govern the design of the output plots

    Attributes:
        group_colors (dict[str, str]): what colors to use for each group in group comparison plots - must have one color per group
        marker_size (int): what size to plot the markers, defaults to 2
        marker_color (str): what color to plot the data (for single animals or single groups), defaults to 'b' (blue)
        individual_model_fit (bool): whether to plot the models on single animal plots, defaults to True
        fit_color (str): what color to plot the model (for single animals or single groups), defaults to 'k' (black)
        alpha (float): transparency to plot the model, defaults to 0.3
        group_error_bars (bool): whether to plot the error bars for group averages, defaults to True
        error_color (str): what color to plot the error bars for group averages, defaults to 'b' (blue)
        n_between_error (int): n to plot error bars on every nth data point, defaults to 1
        group_model_fit (bool): whether to plot the models on group plots, defaults to True
        equation (bool): whether to display the model equation on single animal or single group plots, defaults to True
        display_individual_figures (bool): whether to render the single animal plots, defaults to False
        save_individual_figures (bool): whether to save out the single animal plots, defaults to True
        display_solo_group_figures (bool): whether to render the group plots, defaults to False
        save_solo_group_figures (bool): whether to save out the single group plots, defaults to True
        save_combined_view_figures (bool): whether to save out single group plots that show component individuals, defaults to True
        fig_extension (str): what file format to save plots in, defaults to '.png'
        colormap_name (str): what color map to use for the trajectory plot time bar, defaults to 'gist_rainbow'
        edge_color (str): what color to plot the arena boundary for thr trajectory plot time bar, defaults to 'k' (black)
        error_width (float): what width to plot the error bars, defaults to 0.5
        save_group__comparison_figures (bool): whether to save out the the group comparison plots, defaults to True
    """
    # group_colors
    group_colors: dict[str, str]
    # size for the markers in scatter plots
    marker_size: int = 2
    # individual marker color
    marker_color: str = "b"
    # include model fit?
    individual_model_fit: bool = True
    # individual model color
    fit_color: str = "k"
    # individual model transparency
    alpha: float = 0.3
    # include error bars?
    group_error_bars: bool = True
    # color of group error_bars
    error_color: str = "b"
    # how many points to skip between errors shown
    n_between_error: int = 1
    # include model fits?
    group_model_fit: bool = True
    # include model equations?
    equation: bool = True
    # show the plots from individuals
    display_individual_figures: bool = False
    # save the plots from individuals
    save_individual_figures: bool = True
    # show the plots from solo groups
    display_solo_group_figures: bool = False
    # save the plots from solo groups
    save_solo_group_figures: bool = True
    # save the plots with individual and group combined view
    save_combined_view_figures: bool = True
    # figure format to save in
    fig_extension: str = ".png"
    # which colormap to use for track color bar
    colormap_name: str = "gist_rainbow"
    # what color to plot the arena edge
    edge_color: str = "k"
    # how thick the error bars should be
    error_width: float = 0.5
    # save the plots of group comparisons
    save_group__comparison_figures: bool = True
