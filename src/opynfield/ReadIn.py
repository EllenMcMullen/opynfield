from dataclasses import dataclass, field
import numpy as np
from tkinter import filedialog
import pandas as pd


@dataclass
class Track:
    # dataclass for standardized track after data is read in and wrangled
    group: str  # can change to enum
    x: np.ndarray = field(repr=False)  # x coordinate
    y: np.ndarray = field(repr=False)  # y coordinate
    t: np.ndarray = field(repr=False)  # time
    track_type: str  # which data type this came from -> can change to enum
    options: list
    # for buri: x and y center coordinates (in cm) then arena_radius_cm
    # for ethov1: arena number


def read_buridian(groups_with_file_type, all_tracks, verbose, arena_radius_cm, running_window_length, window_step_size, sample_freq, time_bin_size):
    for buridian_group in groups_with_file_type:
        if verbose:
            print(f'Running Buridian Tracker Files For Group: {buridian_group}')
        title1 = f"Select .dat files in folder for {buridian_group}"
        title2 = f"Select .xml files in folder for {buridian_group}"
        data_files = filedialog.askopenfilenames(filetypes=[("Dat files", "*.dat")], title=title1)
        meta_files = filedialog.askopenfilenames(filetypes=[("xml files", "*.xml")], title=title2)
        for file_num in range(len(data_files)):
            if verbose:
                print(f"{buridian_group}, File{file_num + 1} Out Of {len(data_files)}")
            file_data = pd.read_csv(data_files[file_num], sep='\t', lineterminator='\r')
            file_data = file_data.iloc[0:-2]
            file_meta = meta_files[file_num]
    return
