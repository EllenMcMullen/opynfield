from tkinter import filedialog
import openpyxl as xl
import pandas as pd
from src.opynfield.readin.read_in import Track
import numpy as np
import xlrd


def read_etho_v1(groups_with_file_type: list[str], verbose: bool, sample_freq: int, time_bin_size: int,
                 all_tracks: list[Track]) -> list[Track]:
    for etho_group in groups_with_file_type:
        if verbose:
            print(f'Running Ethovision V1 Tracker Files For Group: {etho_group}')
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
            # track info
            group = sheet['B35'].value
            arena = sheet['B6'].value
            parts = arena.split()
            sheet_num = int(parts[1])  # sheet num indicated which arena it came from
            if verbose:
                print(f"Running Sheet {sheet_num}")
            # track data
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


def read_etho_v2(groups_with_file_type: list[str], verbose: bool, sample_freq: int, time_bin_size: int,
                 all_tracks: list[Track]) -> list[Track]:
    for etho_group in groups_with_file_type:
        if verbose:
            print(f'Running Ethovision V2 Tracker Files For Group: {etho_group}')
    title1 = 'Select all .xls v2 files for this experiment'
    # select excel files for all groups
    all_group_data_files = filedialog.askopenfilenames(filetypes=[("Excel Files", "*.xls *.xlsx")], title=title1,
                                                       multiple=True)
    etho_tracks = list()
    for file_num in range(len(all_group_data_files)):
        file = all_group_data_files[file_num]
        if verbose:
            print(f"Running File {file_num + 1} Out Of {len(all_group_data_files)}")
        wb = xlrd.open_workbook(file)
        # read in each file and sheet's data
        for sheet in wb:
            header_lines = 28
            print('Warning, make sure this file has 28 header lines')
            # track info
            group = sheet[25, 1].value
            arena = sheet[10, 1].value
            parts = arena.split()
            sheet_num = int(parts[1])  # sheet num indicates which arena it came from
            if verbose:
                print(f"Running Sheet {sheet_num}")
            # track data
            x = list()
            y = list()
            t = list()
            for i in range(sheet.nrows):
                t.append(sheet[i, 0].value)
                x.append(sheet[i, 1].value)
                y.append(sheet[i, 2].value)
            time_col = np.array(t[header_lines:sheet.nrows])
            x_col = np.array(x[header_lines:sheet.nrows])
            y_col = np.array(y[header_lines:sheet.nrows])
            track = Track(group, x_col, y_col, time_col, 'Ethovision Excel Version 2', [sheet_num], False)
            # put track coordinates through standardization procedures (for single track)
            track.etho_v2_numeric(verbose)
            track.etho_v2_subsample(sample_freq, time_bin_size, verbose)
            track.etho_v2_fill_missing(verbose)
            etho_tracks.append(track)
    # group tracks by arena and get their center points
    tracks_by_arena = sort_tracks_by_arena(etho_tracks)
    combined_coords_by_arena = combine_arena_coords(tracks_by_arena)
    center_points_by_area = extract_arena_center_point(combined_coords_by_arena, verbose)
    for track in etho_tracks:
        # put track coordinates through standardization procedures (given the arena)
        track.etho_v2_convert_to_center(center_points_by_area, verbose)
        track.standardized = True
        all_tracks.append(track)
    return all_tracks


def read_etho_txt(groups_with_file_type: list[str], verbose: bool, sample_freq: int, time_bin_size: int,
                  all_tracks: list[Track]) -> list[Track]:
    for etho_group in groups_with_file_type:
        if verbose:
            print(f'Running Ethovision Text Tracker Files For Group: {etho_group}')
    title1 = 'Select all .txt files for this experiment'
    # select text files for all groups
    all_group_data_files = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")], title=title1,
                                                       multiple=True)
    etho_tracks = list()
    # need to force column names since data is saved in txt format
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']

    # read in each file's data
    for file_num in range(len(all_group_data_files)):
        file = all_group_data_files[file_num]
        if verbose:
            print(f"Running File {file_num + 1} Out Of {len(all_group_data_files)}")
        df = pd.read_csv(file, encoding='UTF-16', names=labels, sep=',')
        # track info
        header_lines = df['B'][0]  # should be 38
        arena = df['B'][5]
        parts = arena.split()
        sheet_num = int(parts[1])  # sheet num indicates which arena it came from
        group = df['B'][34]
        # track data
        t = df['B'][header_lines:].values
        x = df['C'][header_lines:].values
        y = df['D'][header_lines:].values
        # convert to float
        for c in range(len(t)):
            try:
                t[c] = float(t[c])
                x[c] = float(x[c])
                y[c] = float(y[c])
            except ValueError:
                pass  # nans and blank lines at end of file
        track = Track(group, x, y, t, 'Ethovision Text', [sheet_num], False)
        # put track coordinates through standardization procedures (for single track)
        track.etho_txt_numeric(verbose)
        track.etho_txt_subsample(sample_freq, time_bin_size, verbose)
        track.etho_txt_fill_missing(verbose)
        etho_tracks.append(track)
    # group tracks by arena and get their center points
    tracks_by_arena = sort_tracks_by_arena(etho_tracks)
    combined_coords_by_arena = combine_arena_coords(tracks_by_arena)
    center_points_by_area = extract_arena_center_point(combined_coords_by_arena, verbose)
    for track in etho_tracks:
        # put track coordinates through standardization procedures (given the arena)
        track.etho_txt_convert_to_center(center_points_by_area, verbose)
        track.standardized = True
        all_tracks.append(track)
    return all_tracks


def read_etho_ml(groups_with_file_type: list[str], verbose: bool, sample_freq: int, time_bin_size: int,
                 all_tracks: list[Track]) -> list[Track]:
    for etho_group in groups_with_file_type:
        if verbose:
            print(f'Running Ethovision ML Tracker Files For Group: {etho_group}')
        title1 = f"Select ML .txt files in folder for {etho_group}"
        # select ML .txt files from ethovision
        data_files = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")], title=title1)
        for file_num in range(len(data_files)):
            if verbose:
                print(f"{etho_group}, File{file_num + 1} Out Of {len(data_files)}")
            # this file type lacks the track info, only contains the track data
            file_data = pd.read_csv(data_files[file_num], sep='\t', header=None)
            track = Track(etho_group, file_data[1].values, file_data[2].values, file_data[0].values,
                          'Ethovision Through MATLAB', [], False)
            # put track coordinates through standardization procedures (for single track)
            track.etho_ml_numeric(verbose)
            track.etho_ml_subsample(sample_freq, time_bin_size, verbose)
            track.etho_ml_fill_missing(verbose)
            # since we don't know which arena the track came from, we must calculate the center point
            # from the track's coordinates, rather than combined coordinates
            track_center = calc_center(track.x, track.y, verbose)
            track.etho_ml_convert_to_center(track_center, verbose)
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
