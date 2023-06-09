from dataclasses import dataclass


@dataclass
class PlotSettings:
    # size for the markers in scatter plots
    marker_size: int = 2
    # individual marker color
    marker_color: str = 'b'
    # include model fit?
    individual_model_fit: bool = True
    # individual model color
    fit_color: str = 'k'
    # individual model transparency
    alpha: float = 0.3
    # include error bars?
    group_error_bars: bool = True
    # color of group error_bars
    error_color: str = 'b'
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
    fig_extension: str = '.png'
    # which colormap to use for track color bar
    colormap_name: str = 'gist_rainbow'
    # what color to plot the arena edge
    edge_color: str = 'k'
    # how thick the error bars should be
    error_width: float = 0.5
