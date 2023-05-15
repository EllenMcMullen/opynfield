from src.opynfield.config.user_input import UserInput
from src.opynfield.readin.run_all import run_all_track_types
from src.opynfield.config.defaults_settings import Defaults
from src.opynfield.config.cov_asymptote import CoverageAsymptote
from src.opynfield.calculate_measures.calculate_measures import tracks_to_measures


user_config = UserInput({'Canton S': ['Buridian Tracker'], 'Canton S 2': ['Buridian Tracker']},
                        {'Canton S': 'CS1', 'Canton S 2': 'CS2'}, 4.2, 30, 1, 1, 0.001, True)
track_list = run_all_track_types(user_config.groups_and_types, user_config.verbose, user_config.arena_radius_cm,
                                 user_config.running_window_length, user_config.window_step_size,
                                 user_config.sample_freq, user_config.time_bin_size, user_config.trim)
test_defaults = Defaults()
test_cov_asymptote = CoverageAsymptote()
standard_tracks, tracks_by_groups = tracks_to_measures(track_list, user_config, test_defaults, test_cov_asymptote)
