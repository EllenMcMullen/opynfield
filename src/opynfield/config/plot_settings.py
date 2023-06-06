from dataclasses import dataclass


@dataclass
class PlotSettings:
    # size for the markers in scatter plots
    marker_size: int = 2
    # individual marker color
    marker_color: str = 'b'
    # include model fit?
    model_fit: bool = True
    # individual model color
    fit_color: str = 'k'
    # individual model transparency
    alpha: float = 0.3
    # include error bars?
    error_bars: bool = True
    # include model equations?
    equation: bool = True
    # show the plots from individuals
    display_individual_figures: bool = False
    # save the plots from individuals
    save_individual_figures: bool = True
    # figure format to save in
    fig_extension: str = '.png'
    # which colormap to use for track color bar
    colormap_name = 'gist_rainbow'
    # what color to plot the arena edge
    edge_color = 'k'
