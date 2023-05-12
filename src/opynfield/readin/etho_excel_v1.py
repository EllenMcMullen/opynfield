from tkinter import filedialog
import openpyxl as xl
import pandas as pd
from src.opynfield.readin.read_in import Track


def read_ethov1(groups_with_file_type: list[str], verbose: bool):
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
    return
