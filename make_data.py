import os
from itertools import  groupby
import h5py
from time import sleep
from sudoku_generator import *

import unittest
import numpy as np


class TheoreticalLimit(Exception):
    pass


class GenerationLimit(Exception):
    pass


def make_board(num_clues, single_solution=True):
    """
    Makes a sudoku board with num_clues.
    :raises TheoreticalLimit if 81 < num_clues < 17
    :param num_clues: int number of clues
    :return: np.ndarray shape=(2,) where
            [0] is np.ndarray of shape=(9, 9), dtype='uint8', containing board
            [1] is np.ndarray of shape=(9, 9), dtype='uint8', containing solution
    """
    if not 16 < num_clues < 82:
        raise TheoreticalLimit("17-81 is the theoretical range of clues, but %s were given." % num_clues)

    rows = 'ABCDEFGHI'
    cols = '123456789'

    board_string = random_puzzle(num_clues, single_solution)
    solution_dict = solve(board_string)

    solution_string = ""

    for r in rows:
        solution_string += (''.join(solution_dict[r + c] for c in cols))

    board_uint = np.fromstring(board_string, dtype='uint8').reshape(9, 9)
    solution_uint = np.fromstring(solution_string, dtype='uint8').reshape(9, 9)

    return np.array([board_uint, solution_uint], dtype='uint8')


def make_one_hot(ref_board=None, num_clues=None, single_solution=True):
    """
    Converts an existing ref_board, or a new ref_board with num_clues, to a one_hot representation.
    :raises ValueError if both ref_board and num_clues are not specified
    :param ref_board: np.ndarray of shape,dtype returned from make_board()
    :param num_clues: int number of clues
    :return: np.ndarray shape=(2,) where
            [0] is np.ndarray of shape=(9, 9, 9), dtype='bool', containing board
            [1] is np.ndarray of shape=(9, 9, 9), dtype='bool', containing solution
            where each "cell" is a one_hot vector dim=9
    """
    if ref_board is None and num_clues is None:
        raise ValueError("Must specifiy ref_board or num_clues")
    elif num_clues is not None:
        ref_board = make_board(num_clues=num_clues, single_solution=single_solution)
    onehots = {48: [0, 0, 0, 0, 0, 0, 0, 0, 0],
               49: [1, 0, 0, 0, 0, 0, 0, 0, 0],
               50: [0, 1, 0, 0, 0, 0, 0, 0, 0],
               51: [0, 0, 1, 0, 0, 0, 0, 0, 0],
               52: [0, 0, 0, 1, 0, 0, 0, 0, 0],
               53: [0, 0, 0, 0, 1, 0, 0, 0, 0],
               54: [0, 0, 0, 0, 0, 1, 0, 0, 0],
               55: [0, 0, 0, 0, 0, 0, 1, 0, 0],
               56: [0, 0, 0, 0, 0, 0, 0, 1, 0],
               57: [0, 0, 0, 0, 0, 0, 0, 0, 1]}

    b = []
    for x in range(0, len(ref_board[0])):
        for y in range(0, len(ref_board[0][x])):
            if ref_board[0][x][y] in onehots:
                b.append(onehots[ref_board[0][x][y]])

    b = [b[i:i + 9] for i in range(0, len(b), 9)]
    bool_board = np.array(b, dtype=np.bool)

    s = []
    for x in range(0, len(ref_board[1])):
        for y in range(0, len(ref_board[1][x])):
            if ref_board[1][x][y] in onehots:
                s.append(onehots[ref_board[1][x][y]])

    s = [s[i:i + 9] for i in range(0, len(s), 9)]
    bool_solution = np.array(s, dtype=np.bool)

    return np.array([bool_board, bool_solution], dtype=np.bool)


def make_boards(num_boards, num_clues, one_hot=False, single_solution=True):
    """
    Make num_boards each with num_clues.  If one_hot, return as one_hot boards.
    :raises TheoreticalLimit if not possible to make num_boards with num_clues
    :param num_boards: int number of boards to make
    :param num_clues: int number of clues per board
    :return: np.ndarray shape=(num_boards, 2) where
            [0] is return of make_board() if not one_hot, or make_one_hot() if one_hot
            if one_hot dtype='bool; else dtype='uint8'
    """
    if num_clues < 17:
        raise TheoreticalLimit("17 is the theoretical minimum number of clues, but %s were given." % num_clues)

    else:
        boards = []
        for i in range(0, num_boards):
            if one_hot:
                boards.append(make_one_hot(num_clues=num_clues, single_solution=single_solution))
            else:
                boards.append(make_board(num_clues=num_clues, single_solution=single_solution))
        if one_hot:
            return np.array(boards, dtype=np.bool)
        else:
            return np.array(boards, dtype='uint8')


def make_dataset(num_boards, clues_enum, one_hot=False, name=None, dest=None, single_solution=True,
                 include_solutions=True):
    """
    Creates an hdf5 file with num_boards per num_clues in clues_enum and saves it file name at dest
    :param num_boards: int number of boards per num_clues
    :param clues_enum: enumerable whose entries are num_clues
    :param one_hot: bool, if true make one_hot boards
    :param name: str filename to save to; call name_dataset() if None
    :param dest: str path to save to; use working directory if None
    :param single_solution: bool, if true use only puzzles with a single solution
    :param include_solutions: bool, if true save solutions; if false, leave solutions tables empty
    :return: True if successful

    HDF5 Structure:
    filename.hdf5
        grp: boards
            grp: num_clues
                dset: n rows for n boards
        grp: solutions
            grp: num_clues
                dset: n rows for n boards (empty dset if include_solutions==False)

    Notes:
        - Norvig's generator does not guarantee a single solution puzzle.
        If single_solution==True, verify that a puzzle has only a single solution before including it.
        - An hdf5 file should contain boards of the same one_hot condition (ie all or none).
        dtypes should be as small as possible (int8/bool_)
        - What if n boards are requested for m clues, even though only n-1 boards are possible?
        Whether there is a known limit (i.e. hardcode it) or simply a trial and error (I've tried 20 boards and failed),
        this condition needs to be in there.
        - Don't generate identical boards!
        - Performance is going to be important.  Should verify that:
            - the selected file system has the capacity for the requested dataset
            - the code is dumping to the filesystem periodically (not building the entire thing in memory)
            - regular updates to the user at reasonable intervals for progress and expected time to completion
    """
    if isinstance(clues_enum, (tuple, list, set)):
        clues_enum = [i for i, j in groupby(sorted(clues_enum))]
        if len(clues_enum) == 1:
            clues_enum = int(clues_enum[0][0])

    if isinstance(num_boards, (tuple, list, set)):
        num_boards = int(num_boards[0])

    def check_duplicates(boards):
        for i in range(0, len(boards), 1):
            for j in range(0, len(boards), 1):
                if i != j:
                    if np.array_equal(boards[i], boards[j]):
                        return True
        return False

    def generate_dataset(num_clues):
        inc = 0
        try:
            while True:
                boards = make_boards(num_boards=num_boards, num_clues=num_clues, one_hot=one_hot,
                                     single_solution=single_solution)

                unique_boards = []
                unique_solutions = []
                for i in range(0, boards.shape[0], 1):
                    unique_boards.append(boards[i][0])
                    unique_solutions.append(boards[i][1])

                if check_duplicates(unique_boards) is False:
                    return [unique_boards, unique_solutions]
                else:
                    inc += 1
                    if inc is 20:
                        raise GenerationLimit()
        except GenerationLimit:
            print("Failed 20 times trying to generate %s unique boards with %s clues. Skipping." % (
                num_boards, clues_enum))

    if name is None:
        name = name_dataset(num_boards=num_boards, clues_enum=clues_enum, one_hot=one_hot)

    if dest is None:
        dest = os.path.dirname(os.path.realpath('make_data.py'))

    if isinstance(clues_enum, int):
        if os.path.exists(os.path.join(dest, name + '.hdf5')):
            os.remove(os.path.join(dest, name + '.hdf5'))
        hdf5 = h5py.File(os.path.join(dest, name + '.hdf5'))

        print('\rGenerating dataset 1 / 1 [Clues:%s]...' % (str(clues_enum)), end='')
        dataset = generate_dataset(clues_enum)

        dataset_boards = dataset[0]
        dataset_solutions = np.empty((1,), dtype='uint8')

        if include_solutions is True:
            dataset_solutions = dataset[1]

        print('\rSaving dataset 1 / 1 [Clues:%s]...' % (str(clues_enum)), end='')
        sleep(1)

        hdf5.create_dataset('boards/' + str(clues_enum), data=dataset_boards)
        hdf5.create_dataset('solutions/' + str(clues_enum), data=dataset_solutions)
        hdf5.close()

    elif isinstance(clues_enum, (tuple, list, set)):
        if os.path.exists(os.path.join(dest, name + '.hdf5')):
            os.remove(os.path.join(dest, name + '.hdf5'))
        for i in range(0, len(clues_enum), 1):
            hdf5 = h5py.File(os.path.join(dest, name + '.hdf5'))

            print('\rGenerating dataset %s / %s [Clues:%s]...' % (str(i + 1), str(len(clues_enum)), str(clues_enum[i])),
                  end='')

            dataset = generate_dataset(clues_enum[i])

            dataset_boards = dataset[0]
            dataset_solutions = np.empty((1,), dtype='uint8')

            if include_solutions is True:
                dataset_solutions = dataset[1]

            print('\rSaving dataset %s / %s [Clues:%s]...' % (str(i + 1), str(len(clues_enum)), str(clues_enum[i])),
                  end='')
            sleep(1)

            hdf5.create_dataset('boards/' + str(clues_enum[i]), data=dataset_boards)
            hdf5.create_dataset('solutions/' + str(clues_enum[i]), data=dataset_solutions)
            hdf5.close()

    else:
        raise ValueError('Unknown type for clue_enum. Correct the query and try again.')

    return True


def name_dataset(num_boards, clues_enum, one_hot):
    if one_hot:
        l = 'one_hot'
    else:
        l = 'int'
    return ("%sx%d_%s" % (str(clues_enum), int(num_boards), l)).replace(' ', '')


class TestMakeData(unittest.TestCase):
    def setUp(self):
        pass

    def test_make_board(self):
        self.assertRaises(TheoreticalLimit, lambda: make_board(16))
        test_board = make_board(50)
        self.assertEqual(test_board.shape, (2, 9, 9))
        self.assertEqual(test_board.dtype, 'uint8')
        self.assertEqual(test_board[0].shape, (9, 9))
        self.assertEqual(test_board[0].dtype, 'uint8')
        self.assertEqual(test_board[1].shape, (9, 9))
        self.assertEqual(test_board[1].dtype, 'uint8')

    def test_make_one_hot(self):
        self.assertRaises(ValueError, lambda: make_one_hot(ref_board=None, num_clues=None))
        test_board_a = make_one_hot(num_clues=50)
        self.assertEqual(test_board_a.shape, (2, 9, 9, 9))
        self.assertEqual(test_board_a.dtype, 'bool')
        self.assertEqual(test_board_a[0].shape, (9, 9, 9))
        self.assertEqual(test_board_a[0].dtype, 'bool')
        self.assertEqual(test_board_a[1].shape, (9, 9, 9))
        self.assertEqual(test_board_a[1].dtype, 'bool')

        test_board_b = make_one_hot(ref_board=make_board(50))
        self.assertEqual(test_board_b.shape, (2, 9, 9, 9))
        self.assertEqual(test_board_b.dtype, 'bool')
        self.assertEqual(test_board_b[0].shape, (9, 9, 9))
        self.assertEqual(test_board_b[0].dtype, 'bool')
        self.assertEqual(test_board_b[1].shape, (9, 9, 9))
        self.assertEqual(test_board_b[1].dtype, 'bool')

    def test_make_boards(self):
        self.assertRaises(TheoreticalLimit, lambda: make_boards(1, 16))

        test_a = make_boards(10, 50, one_hot=False)
        self.assertEqual(test_a.shape, (10, 2, 9, 9))
        self.assertEqual(test_a.dtype, 'uint8')

        test_b = make_boards(10, 50, one_hot=True)
        self.assertEqual(test_b.shape, (10, 2, 9, 9, 9))
        self.assertEqual(test_b.dtype, 'bool')

    def test_name_dataset(self):
        self.assertEqual(name_dataset(10, [20, 30, 40, 50], True),
                         '[20,30,40,50]x10_one_hot')
        self.assertEqual(name_dataset(10, [20, 30, 40, 50], False),
                         '[20,30,40,50]x10_int')

    def test_make_dataset(self):
        self.assertRaises(ValueError, lambda: make_dataset(10, 'error', one_hot=False, name='test_data'))
        self.assertRaises(ValueError, lambda: make_dataset(10, [50, 50], one_hot=False, name='test_data'))

        self.assertTrue(make_dataset(10, [50, 55], one_hot=False, name='test_data'))

        hdf5 = h5py.File('test_data.hdf5')

        test_a = hdf5['boards/50'][:]
        self.assertEqual(test_a.shape, (10, 9, 9))
        self.assertEqual(test_a.dtype, 'uint8')
        test_board_a = test_a[0]
        self.assertEqual(test_board_a.shape, (9, 9))
        self.assertEqual(test_board_a.dtype, 'uint8')

        test_b = hdf5['boards/55'][:]
        self.assertEqual(test_b.shape, (10, 9, 9))
        self.assertEqual(test_b.dtype, 'uint8')
        test_board_b = test_b[0]
        self.assertEqual(test_board_b.shape, (9, 9))
        self.assertEqual(test_board_b.dtype, 'uint8')

        test_a = hdf5['solutions/50'][:]
        self.assertEqual(test_a.shape, (10, 9, 9))
        self.assertEqual(test_a.dtype, 'uint8')
        test_board_a = test_a[0]
        self.assertEqual(test_board_a.shape, (9, 9))
        self.assertEqual(test_board_a.dtype, 'uint8')

        test_b = hdf5['solutions/55'][:]
        self.assertEqual(test_b.shape, (10, 9, 9))
        self.assertEqual(test_b.dtype, 'uint8')
        test_board_b = test_b[0]
        self.assertEqual(test_board_b.shape, (9, 9))
        self.assertEqual(test_board_b.dtype, 'uint8')

        hdf5.close()

        self.assertTrue(make_dataset(10, 45, one_hot=False, name='test_data'))

        hdf5 = h5py.File('test_data.hdf5')

        test = hdf5['boards/45'][:]
        self.assertEqual(test.shape, (10, 9, 9))
        self.assertEqual(test.dtype, 'uint8')
        test_board = test[0]
        self.assertEqual(test_board.shape, (9, 9))
        self.assertEqual(test_board.dtype, 'uint8')

        test = hdf5['solutions/45'][:]
        self.assertEqual(test.shape, (10, 9, 9))
        self.assertEqual(test.dtype, 'uint8')
        test_board = test[0]
        self.assertEqual(test_board.shape, (9, 9))
        self.assertEqual(test_board.dtype, 'uint8')

        hdf5.close()

        self.assertTrue(make_dataset(10, [50, 55], one_hot=True, name='test_data'))

        hdf5 = h5py.File('test_data.hdf5')

        test_a = hdf5['boards/50'][:]
        self.assertEqual(test_a.shape, (10, 9, 9, 9))
        self.assertEqual(test_a.dtype, 'bool')
        test_board_a = test_a[0]
        self.assertEqual(test_board_a.shape, (9, 9, 9))
        self.assertEqual(test_board_a.dtype, 'bool')

        test_b = hdf5['boards/55'][:]
        self.assertEqual(test_b.shape, (10, 9, 9, 9))
        self.assertEqual(test_b.dtype, 'bool')
        test_board_b = test_b[0]
        self.assertEqual(test_board_b.shape, (9, 9, 9))
        self.assertEqual(test_board_b.dtype, 'bool')

        test_a = hdf5['solutions/50'][:]
        self.assertEqual(test_a.shape, (10, 9, 9, 9))
        self.assertEqual(test_a.dtype, 'bool')
        test_board_a = test_a[0]
        self.assertEqual(test_board_a.shape, (9, 9, 9))
        self.assertEqual(test_board_a.dtype, 'bool')

        test_b = hdf5['solutions/55'][:]
        self.assertEqual(test_b.shape, (10, 9, 9, 9))
        self.assertEqual(test_b.dtype, 'bool')
        test_board_b = test_b[0]
        self.assertEqual(test_board_b.shape, (9, 9, 9))
        self.assertEqual(test_board_b.dtype, 'bool')

        hdf5.close()

        self.assertTrue(make_dataset(10, 45, one_hot=True, name='test_data'))

        hdf5 = h5py.File('test_data.hdf5')

        test = hdf5['boards/45'][:]
        self.assertEqual(test.shape, (10, 9, 9, 9))
        self.assertEqual(test.dtype, 'bool')
        test_board = test[0]
        self.assertEqual(test_board.shape, (9, 9, 9))
        self.assertEqual(test_board.dtype, 'bool')

        test = hdf5['solutions/45'][:]
        self.assertEqual(test.shape, (10, 9, 9, 9))
        self.assertEqual(test.dtype, 'bool')
        test_board = test[0]
        self.assertEqual(test_board.shape, (9, 9, 9))
        self.assertEqual(test_board.dtype, 'bool')

        hdf5.close()

        self.assertTrue(make_dataset(10, 40, one_hot=False, name='test_data', include_solutions=False))

        hdf5 = h5py.File('test_data.hdf5')

        test = hdf5['solutions/40'][:]
        self.assertEqual(test, np.array([0], dtype='uint8'))

        hdf5.close()

        self.assertTrue(os.path.exists('test_data.hdf5'))
        if os.path.exists('test_data.hdf5'):
            os.remove('test_data.hdf5')

    def tearDown(self):
        pass


if __name__ == '__main__':
    # TODO executable interface
    # If no args, run the unittests (unless we move unittesting to another file, in which case do nothing)
    # Otherwise, have a standard interface for calling make_dataset(), with all the necessary parameters
    unittest.main(verbosity=2)

