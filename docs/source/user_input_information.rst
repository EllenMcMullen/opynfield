user input information
======================

The user inputs needed to analyze open field exploration data using the opynfield package are divided into five groups based on the aspects of analysis that the settings control, and based on the likelihood that a user would need to adjust these settings from their default values.

User Inputs
=============
The UserInput dataclass contains all of the settings that are necessary to read the tracking data into the opynfield Track format, as well as settings that must be changed for each analysis.

1. ``groups_and_types`` contains the names of the groups that you will be analyzing as well as the filetypes that each group was recorded in. It is a dictionary where the keys are the group names (strings) and the values are a list of filetypes (strings). For example, if you have two groups and their tracks were recorded using both Buridian Tracker and Ethovision, your ``groups_and_types`` should be: {'GroupA': ["Buridian Tracker", "Ethovision Excel Version 2"], 'GroupB': ["Buridian Tracker", "Ethovision Excel Version 2"]}. Valid filetypes include: 'Buridian Tracker', 'Ethovision Excel Version 1', 'Ethovision Excel Version 2', 'Ethovision Text', 'Ethovision Through MATLAB', 'AnyMaze Center', and 'AnyMaze Head'. If your experiment includes track types 'Ethovision Excel Version 1', 'Ethovision Excel Version 2', or 'Ethovision Text', then the group names you provide must match the group names that are recorded in the Ethovision data sheets.
2. ``groups_to_paths`` contains the names of the groups that you provided in ``groups_and_types`` as well as alternate group names that exclude any special characters. This is needed so that we are able to save results with the group name in the file name. It is a dictionary where the keys are the original group names (strings), and the values are the alternate group names (strings) For example if your groups are names by geneotype, you must remove and / characters like {'w-': 'white', 'w-/+': 'heterozygote', '+/+': 'wildtype'}. If your group names have no special characters, you can just provide the same group names (e.g. {'GroupA': 'GroupA', 'GroupB': 'GroupB'}).
3. ``arena_radius_cm`` contains the radius of the arena in which the tracks were recorded. It is a float. This is needed for Buridian Tracker and Anymaze Tracker filetypes, which record animal position in pixels rather than centimeters. Right now this is a global parameter (i.e. you cannot read in tracks with two different arena sizes at once).
4. ``sample_freq`` contains the recording frame rate (in Hz) for the tracks. It is an integer. Right now this is a global parameter (i.e. you cannot read in tracks with two different frame rates at once).
5. ``edge_dist_cm`` contains the distance from the boundary of the arena which should be considered the edge region. It is a float. With *Drosophila* we have often used 0.5cm or more commonly 1cm. With other taxa it may be necessary to try several different values and see which ensures the animals spend enough time in the arena edge. Right now this is a global parameter (i.e. you cannot read in tracks with two different edge distances at once).
6. ``time_bin_size`` contains the amount of time (in seconds) that should be aggregated into one point. It allows us to change the density of the data from ``sample_freq`` points per second to 1/``time_bin_size`` samples per second. It is an interger.
7. ``inactivity_threshold`` contains the threshold at which we should consider a movement too small to be an actual step by the animal, and instead attribute it to body wobble. It is a float.
8. ``verbose`` indicates whether or not we want progress updates displayed as the analysis is running. It is a boolean.
9. ``result_path`` contains the path to where we want to save the results of the analysis. It is a string.
10. ``running_window_length`` is a parameter of the smoothing function that is implemented on the non-Ethovision recording types. The smoothing finction is essentiall a weighted running average, and ``running_window_length`` indicates how many points should be contained in the window for the average. It must be an odd integer and defaults to 5 in order to match the native Ethovision smoothing function.
11. ``window_step_size`` is a parameter of the smoothing function that is implemented on the non-Ethovision recording types. The smoothing finction is essentiall a weighted running average, and ``window_step_size`` indicates how many points the averaging window should move forward between each average. It is an integer and defaults to 1 in order to match the native Ehtovision smoothing function.
12. ``trim`` indicates how many recording points it takes for the aninal to be placed in the arena. It is important for Anymaze data in order to correctly impute the arena boundary. It is an interger and defaults to 0, but should be increased for Anymaze tracking data.
13. ``bound_level`` indicates how many standard deviations away from the mean we should consider to be an outlier parameter value. It is a float and defualts to 2.0. (95% threshold)

Coverage Asymptote Settings
=============================
The CoverageAsymptote dataclass contains information on how to fit a time vs coverage model in order to calculate the asymptote coverage value for either an individual or a group.

1. ``f_name`` is which functional form to use in fitting the time vs coverage model. It defaults to the fixed exponential model (y = a*(e^b*x-1))
2. ``asymptote_param`` is which parameter of the model indicates the asymptote magnitude. It defaults to 0 (the first parameter, a in the fixed exponential model)
3. ``asymptote_sign`` indicates the sign that the asymptote parameter is expected to be. It defaults to -1.
4. ``initial_parameters`` provide initial parameter values to use when fitting the model, defaults to (-0.1, -0.1)
5. ``parameter_bounds`` provide first order bounds to ensure that appropriately signed parameters are fit, defaults to ([-10, -10], [0, 0])
6. ``max_f_eval`` indicates how many iterations are allowed before assuming non-convergence, defualts to 4000

Model Fit Settings
====================
The ModelSpecification dataclass contains

1. ``axes`` which x-measure and which y-measure are being fit
2. ``model`` what model will be used to fit that x and y relationship

The model can be one of 4 options: ExponentialModel, FixedExponentialModel, LinearIncreaseModel, LinearDecreaseModel. Each of these in turn is a dataclass that contains information about how to fit that model.

1. ``initial_params`` provide initial parameter values to use when fitting the model, defaults vary by model type
2. ``bounds`` provied first order bounds to ensure that appropriately signed parameters are fit, defaults vary by model type
3. ``max_eval`` indicates how many interactions are allowed before assuming non-convergence, defaults to 4000 in all model types
4. ``display_parts`` provides string components that can be joined with the parameter fits to properly display the fit equation, defaults vary by model type

Plot Settings
===============
The PlotSettings dataclass contains all of the settings that are necessary for the plots that are generated by opynfield.

1. ``group_colors`` is the only mandatory input to PlotSettings. It dictates which colors should be used for which groups in the plots. It is a dictionary where the keys are the group names (strings) provided in the ``groups_and_types`` attribute of a UserInput instance, and the values are the color codes (strings) for which color to plot. For example if you want one group to be plotted in blue and one group to be plotted in green, you could provide {'GroupA': 'b', 'GroupB': 'g'}
2. ``marker_size`` is the size of the markers used in the scatter plots, defaults to 2
3. ``marker_color`` is the color that the markers should be in the individual scatter plots (in group comparison plots, color is determined by ``group_colors``), defaults to 'b' for blue
4.``individual_model_fit`` indicates whether or not the model fit for individual plots should be displayed, defaults to True
5. ``fit_color`` is the color that the individual model fit should be, if displayed, defaults to 'k' (black)
6. ``alpha`` is the transparency level that the model fit for individuals should be displayed with, defaults to 0.3 (0 is completely transparent and 1 is completely opaque)
7. ``group_error_bars`` indicates whether or not the error bars on group averages should be displayed, defaults to True
8. ``error_color`` indicates that color group error bars on single group plots should be, defualts to 'b' (blue), in group comparison plots, color is determined by ``group_colors``
9. ``n_between_error`` indicates how many points to skip between displaying error bars, defaults to 1 (error bars are put on every marker)
10. ``group_model_fit`` indicates whether or not the group model fit should be displayed, defaults to True
11. ``equation`` indicates whether or not the equation of the model fit should be displayed on single group or individual plots, defaults to True
12. ``display_individual_figures`` indicates whether the individual plots should be rendered, defaults to False
13. ``save_individual_figures`` indicates whether the individual plots should be saved out, defaults to True
14. ``display_solo_group_figures`` indicates whether the single group plots should be rendered, defaults to False
15. ``save_solo_group_figures`` indicates whether the single group plots should be saved out, defaults to True
16. ``save_combined_view_figures`` indicates whether the single group average and component individual plots should be saved out, defaults to True
17. ``fig_extension`` provides what file format the plots should be saved in, defaults to .png
18. ``colormap_name`` provides the color map scheme to use in the track trace time bar, defaults to 'gist_rainbow'
19. ``edge_color`` provides the color to use to plot the arena boundary in the track trace, defaults to 'k' (black)
20. ``error_width`` indicates how thick the error bar should be in group plots, defaults to 0.5
21. ``save_group__comparison_figures``  indicates whether the group comparison plots should be saved out, defaults to True

Default Settings
==================
The Defaults dataclass contains the rest of the settings, that typically should not need to be changed by the user.

1. ``node_size`` indicates the angle that defines the circle sector size to divide the arena edge into bins for coverage, defaults to 0.1
2. ``save_group_csvs`` indicates whether or not to save a .csv file for each calculated measure for each group, defaults to True
3. ``save_all_group_csvs`` indicates whether or not to save a .csv file for each calculated measure for all groups together, a helpful format to export for statistical tests in other programs, defaults to True, save_group_csvs must be True for save_all_group_csvs to be True
4. ``save_group_model_csvs`` indicates whether or not to save a .csv file that includes the individuals' fitted parameters for each group, defaults to True
5. ``save_all_group_model_csvs`` indicates whether or not to save a .csv file that includes the individuals' fitted parameters for all groups together, a helpful format to export for statistical tests in other programs, defaults to True
6. ``n_points_coverage`` number of points to group together in an average for coverage, defaults to 36
7. ``n_points_pica`` number of points to group together in an average for PICA, defaults to 36
8. ``n_points_pgca`` number of points to group together in an average for PGCA, defaults to 36
9. ``n_bins_percent_coverage`` number of bins to group together in an average for percent coverage, defaults to 10
10. ``time_averaged_measures`` measures average by time, defaults to ["r", "activity", "p_plus_plus", "p_plus_minus", "p_plus_zero", "p_zero_plus", "p_zero_zero", "coverage", "percent_coverage", "pica", "pgca", "p_plus_plus_given_plus", "p_plus_minus_given_plus", "p_plus_zero_given_plus", "p_zero_plus_given_zero", "p_zero_zero_given_zero", "p_plus_plus_given_any", "p_plus_minus_given_any", "p_plus_zero_given_any", "p_zero_plus_given_any", "p_zero_zero_given_any"]
11. ``coverage_averaged_measures`` measures to average by coverage, defaults to ["activity", "p_plus_plus", "p_plus_minus", "p_plus_zero", "p_zero_plus", "p_zero_zero", "p_plus_plus_given_plus", "p_plus_minus_given_plus", "p_plus_zero_given_plus", "p_zero_plus_given_zero", "p_zero_zero_given_zero", "p_plus_plus_given_any", "p_plus_minus_given_any", "p_plus_zero_given_any", "p_zero_plus_given_any", "p_zero_zero_given_any"]
