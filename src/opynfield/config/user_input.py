from dataclasses import dataclass
import os


@dataclass
class UserInput:
    """This dataclass defines many user inputs that are needed to properly read in and analyze the data

    Attributes:
        groups_and_types (dict[str, list[str]): dictionary of group names to a list of filetypes that include tracks from that group
        groups_to_paths (dict[str, str]): if the group names include non-standard characters (e.g. '/'), how to display the group names without those nonstandard characters
        arena_radius_cm (dict[str, str]): radius of the arena the tracks were recorded in (in cm)
        sample_freq (int): the frame rate that tracking points were recorded with
        edge_dist_cm (float): how far into the arena is considered the edge region
        time_bin_size (int): how many seconds should be binned together in the aggregation
        inactivity_threshold (float): how small of a step should be considered body wobble rather than activity
        verbose (bool): whether to display progress updates
        result_path (str): path to folder where you want to store results
        running_window_length (int): smoothing function parameter set to match ethovision smoothing, defaults to 5
        window_step_size (int): smoothing function parameter set to match ethovision smoothing, defaults to 1
        trim (int): for recordings that start before the animal is in the arena, how many points to trim off the beginning so that the arena boundary is identified correctly, defaults to 0
        bound_level (float): how many standard deviations to use when bounding the parameters fits, defaults to 2
    """
    # key for group names, value for list of file_types that group was recorded with
    groups_and_types: dict[str, list[str]]
    # key for group names as found in data files, value for a variation of that name without forbidden characters
    groups_to_paths: dict[str, str]
    # radius of arena
    arena_radius_cm: float
    # frame rate for your tracking coordinates
    sample_freq: int
    # how far into the arena should we consider the 'edge'
    edge_dist_cm: float
    # how many seconds should we bin together to aggregate
    time_bin_size: int
    # how small of a step should we consider body wobble rather than activity
    inactivity_threshold: float
    # do you want to display progress updates
    verbose: bool
    # path to folder where you will store results
    result_path: str
    # smoothing function parameter set to match ethovision
    running_window_length: int = 5
    # smoothing function parameter set to match ethovision
    window_step_size: int = 1
    # how many points until animal is in the arena
    trim: int = 0
    # how many stds to bound parameter fits to
    bound_level: float = 2

    def set_edge_radius(self):
        """This method takes the arena radius and the edge distance to calculate the edge radiusd

        :return: the radius at which the arena edge region begins
        :rtype: float
        """
        edge_radius = self.arena_radius_cm - self.edge_dist_cm
        return edge_radius

    def change_running_window_length(self, new_window_length):
        """This method allows the running window length to be changed"""
        self.running_window_length = new_window_length

    def change_window_step_size(self, new_window_step_size):
        """This method allows the window step size to be changed"""
        self.window_step_size = new_window_step_size

    def change_trim(self, new_trim):
        """This method allows the trim parameter to be changed"""
        self.trim = new_trim

    def prep_directory(self):
        """This method creates the folder in which the results will be saved"""
        os.makedirs(self.result_path, exist_ok=True)
