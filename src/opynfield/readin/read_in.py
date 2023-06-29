from opynfield.readin import buridian_tracker
from opynfield.readin import etho_tracker
from opynfield.readin import anymaze_tracker

from opynfield.readin.track import Track


def read_track_types(file_type: str, groups_with_file_type: list[str], verbose: bool, arena_radius_cm: float,
                     running_window_length: int, window_step_size: int, sample_freq: int, time_bin_size: int,
                     trim, all_tracks: list[Track]) -> list[Track]:
    if file_type == 'Buridian Tracker':
        all_tracks = buridian_tracker.read_buridian(groups_with_file_type, verbose, arena_radius_cm,
                                                    running_window_length, window_step_size, sample_freq,
                                                    time_bin_size, all_tracks)
    if file_type == 'Ethovision Excel Version 1':
        all_tracks = etho_tracker.read_etho_v1(groups_with_file_type, verbose, sample_freq, time_bin_size, all_tracks)
    if file_type == 'Ethovision Excel Version 2':
        all_tracks = etho_tracker.read_etho_v2(groups_with_file_type, verbose, sample_freq, time_bin_size, all_tracks)
    if file_type == 'Ethovision Text':
        all_tracks = etho_tracker.read_etho_txt(groups_with_file_type, verbose, sample_freq, time_bin_size, all_tracks)
    if file_type == 'Ethovision Through MATLAB':
        all_tracks = etho_tracker.read_etho_ml(groups_with_file_type, verbose, sample_freq, time_bin_size, all_tracks)
    if file_type == 'AnyMaze Center':
        all_tracks = anymaze_tracker.read_anymaze_center(groups_with_file_type, verbose, arena_radius_cm,
                                                         running_window_length, window_step_size, sample_freq,
                                                         time_bin_size, trim, all_tracks)
    if file_type == 'AnyMaze Head':
        all_tracks = anymaze_tracker.read_anymaze_head(groups_with_file_type, verbose, arena_radius_cm,
                                                       running_window_length, window_step_size, sample_freq,
                                                       time_bin_size, trim, all_tracks)

    return all_tracks
