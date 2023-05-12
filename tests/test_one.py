from opynfield.readin.read_in import Track
import numpy as np


def test_track():
    x = Track('Canton S',
              np.array([1, 1, 1, 1, 1]),
              np.array([1, 2, 3, 4, 5]),
              np.array([1, 2, 3, 4, 5]),
              'Buridian Tracker', [], False)
    x.buri_convert_to_center(2, 2, True)
    assert True


def test():
    assert 1 == 1


def test_2():
    assert 1 == 5
