from tkinter import filedialog
import openpyxl as xl
import pandas as pd
from src.opynfield.readin.read_in import Track
import numpy as np


def read_ethov1(groups_with_file_type: list[str], verbose: bool, sample_freq: int, time_bin_size: int,
                all_tracks: list[Track]) -> list[Track]:
    for etho_group in groups_with_file_type:
        if verbose:
            print(f'Running Buridian Tracker Files For Group: {etho_group}')
        title1 = 'Select all .xls v1 files for this experiment'
        # select excel files for all groups
        all_group_data_files = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xls *.xlsx")], title=title1,
                                                           multiple=True)
        etho_tracks = list()
        for file_num in range(len(all_group_data_files)):
            file = all_group_data_files[file_num]
            if verbose:
                print(f"Running File {file_num + 1} Out Of {len(all_group_data_files)}")
            wb = xl.load_workbook(file)
            # read in each file and sheet's data
            for sheet in wb:
                header_lines = int(sheet['B1'].value)
                group = sheet['B35'].value
                arena = sheet['B6'].value
                parts = arena.split()
                sheet_num = int(parts[1])
                if verbose:
                    print(f"Running Sheet {sheet_num}")
                df = pd.DataFrame(sheet.values)
                time_col = df[1][header_lines:]
                x_col = df[2][header_lines:]
                y_col = df[3][header_lines:]
                if y_col[38] is None:
                    print(f"No data in file {file_num + 1} sheet {sheet_num}")
                else:
                    track = Track(group, x_col.values, y_col.values, time_col.values, 'Ethovision Excel Version 1',
                                  [sheet_num], False)
                    # put track coordinates through standardization procedures (for single track)
                    track.etho_v1_numeric(verbose)
                    track.etho_v1_subsample(sample_freq, time_bin_size, verbose)
                    track.etho_v1_fill_missing(verbose)
                    etho_tracks.append(track)
        # group tracks by arena and get their center points
        tracks_by_arena = sort_tracks_by_arena(etho_tracks)
        combined_coords_by_arena = combine_arena_coords(tracks_by_arena)
        center_points_by_area = extract_arena_center_point(combined_coords_by_arena, verbose)
        for track in etho_tracks:
            # put track coordinates through standardization procedures (given the arena)
            track.etho_v1_convert_to_center(center_points_by_area, verbose)
            track.standardized = True
            all_tracks.append(track)
    return all_tracks


def sort_tracks_by_arena(list_of_etho_tracks: list[Track]) -> dict[str: list[Track]]:
    tracks_by_arena = dict()
    for track in list_of_etho_tracks:
        if track.options[0] not in tracks_by_arena:
            # if there hasn't been a track from that arena, add the arena to the dict with that track
            tracks_by_arena[track.options[0]] = [track]
        else:
            # if there are already tracks from that arena, add the track to the list of tracks from that arena
            tracks_by_arena[track.options[0]].append(track)
    return tracks_by_arena


def combine_arena_coords(tracks_by_arena: dict[str: list[Track]]) -> dict[str: tuple[np.ndarray, np.ndarray]]:
    combined_coords_by_arena = dict()
    for arena in tracks_by_arena:
        # the first track initializes the combined coordinates
        combined_x = tracks_by_arena[arena][0].x
        combined_y = tracks_by_arena[arena][0].y
        for track_num in range(1, len(tracks_by_arena[arena])):
            # for the rest of the tracks
            combined_x = np.append(combined_x, tracks_by_arena[arena][track_num].x)
            combined_y = np.append(combined_y, tracks_by_arena[arena][track_num].y)
        # once all tracks run in that arena are added, save them to the dict
        combined_coords_by_arena[arena] = (combined_x, combined_y)
    return combined_coords_by_arena


def extract_arena_center_point(combined_coords_by_arena: dict[str: tuple[np.ndarray, np.ndarray]],
                               verbose: bool) -> dict[str: tuple[float, float]]:
    center_points_by_area = dict()
    for arena in combined_coords_by_arena:
        # for each arena, calculate the center point from the combined coordinates of all tracks run in that arena
        center_point = calc_center(combined_coords_by_arena[arena][0], combined_coords_by_arena[arena][1], verbose)
        if verbose:
            print(f'Arena {arena} Center Point: {center_point}')
        center_points_by_area[arena] = center_point
    return center_points_by_area


def calc_center(combined_x: np.ndarray, combined_y: np.ndarray, verbose: bool) -> tuple[float, float]:
    # this is a rough calculation of the center point
    # would be better to calculate a minimum enclosing circle and compare rough to precise calc
    x_cen_rough = np.nanmin(combined_x) + ((np.nanmax(combined_x) - np.nanmin(combined_x)) / 2)
    y_cen_rough = np.nanmin(combined_y) + ((np.nanmax(combined_y) - np.nanmin(combined_y)) / 2)
    if verbose:
        print('Combined Coordinate Center Point Calculated')
    return x_cen_rough, y_cen_rough
