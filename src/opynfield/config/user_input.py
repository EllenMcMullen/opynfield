from dataclasses import dataclass


@dataclass
class UserInput:
    # key for group names, value for list of file_types that group was recorded with
    groups_and_types: dict[str: list[str]]
    # key for group names as found in data files, value for a variation of that name without forbidden characters
    groups_to_paths: dict[str: str]
    # radius of arena
    arena_radius_cm: float
    # frame rate for your tracking coordinates
    sample_freq: int
    # how far into the arena should we consider the 'edge'
    edge_dist_cm: int
    # how many seconds should we bin together to aggregate
    time_bin_size: int
    # how small of a step should we consider body wobble rather than activity
    inactivity_threshold: float
    # do you want to display progress updates
    verbose: bool
    # smoothing function parameter set to match ethovision
    running_window_length: int = 5
    # smoothing function parameter set to match ethovision
    window_step_size: int = 1
    # how many points until animal is in the arena
    trim: int = 0

    def set_edge_radius(self):
        edge_radius = self.arena_radius_cm - self.edge_dist_cm
        return edge_radius

    def change_running_window_length(self, new_window_length):
        self.running_window_length = new_window_length

    def change_window_step_size(self, new_window_step_size):
        self.window_step_size = new_window_step_size

    def change_trim(self, new_trim):
        self.trim = new_trim
