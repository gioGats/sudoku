import os
from norvig_sudoku import NorvigCode

import numpy as np


class TheoreticalLimit(Exception):
    pass

def make_board(num_clues):
    """
    Makes a sudoku board with num_clues.
    :raises TheoreticalLimit if num_clues < 17
    :param num_clues: int number of clues
    :return: np.ndarray shape=(2,) where
            [0] is np.ndarray of shape=(9, 9), dtype='uint8', containing board
            [1] is np.ndarray of shape=(9, 9), dtype='uint8', containing solution
    """
    if num_clues < 17:
        raise TheoreticalLimit("17 is the theoretical minimum number of clues")

    rows = 'ABCDEFGHI'
    cols = '123456789'

    board_string = NorvigCode().random_puzzle(num_clues)
    solution_dict = NorvigCode().solve(board_string)

    if solution_dict is False:
        while True:
            board_string = NorvigCode().random_puzzle(num_clues)
            solution_dict = NorvigCode().solve(board_string)
            if solution_dict is not False:
                break

    solution_string = ""

    for r in rows:
        solution_string += (''.join(solution_dict[r + c] for c in cols))

    board_uint = np.fromstring(board_string, dtype='uint8').reshape(9, 9)
    solution_uint = np.fromstring(solution_string, dtype='uint8').reshape(9, 9)

    return np.array([board_uint, solution_uint], dtype='uint8')


def make_one_hot(ref_board=None, num_clues=None):
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
        ref_board = make_board(num_clues=num_clues)
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


def make_boards(num_boards, num_clues, one_hot=False):
    """
    Make num_boards each with num_clues.  If one_hot, return as one_hot boards.
    :raises TheoreticalLimit if not possible to make num_boards with num_clues
    :param num_boards: int number of boards to make
    :param num_clues: int number of clues per board
    :return: np.ndarray shape=(num_boards, 2) where
            [0] is return of make_board() if not one_hot, or make_one_hot() if one_hot
            if one_hot dtype='bool; else dtype='uint8'
    """
    boards = []
    for i in range(0, num_boards):
        if one_hot:
            boards.append(make_one_hot(num_clues=num_clues))
        else:
            boards.append(make_board(num_clues=num_clues))
    if one_hot:
        return np.array(boards, dtype=np.bool)
    else:
        return np.array(boards, dtype='uint8')


def make_dataset(num_boards, clues_enum, one_hot=False, name=None, dest=None):
    """
    Creates an hdf5 dataset with num_boards per num_clues in clues_enum and saves it file name at dest
    :param num_boards: int number of boards per num_clues
    :param clues_enum: enumerable whose entries are num_clues
    :param one_hot: bool, if true make one_hot boards
    :param name: str filename to save to; call name_dataset() if None
    :param dest: str path to save to; use working directory if None
    :return: True if successful
    """
    # FUTURE Wait to implement
    raise NotImplementedError


def name_dataset(num_boards, clues_enum, one_hot):
    if one_hot:
        l = 'one_hot'
    else:
        l = 'int'
    return ("%sx%d_%s" % (str(clues_enum), num_boards, l)).replace(' ', '')


if __name__ == '__main__':
    import unittest


    class TestMakeData(unittest.TestCase):
        def setUp(self):
            pass

        def test_make_board(self):
            self.assertRaises(TheoreticalLimit, lambda: make_board(16))
            test_board = make_board(30)
            self.assertEqual(test_board.shape, (2, 9, 9))
            self.assertEqual(test_board.dtype, 'uint8')
            self.assertEqual(test_board[0].shape, (9, 9))
            self.assertEqual(test_board[0].dtype, 'uint8')
            self.assertEqual(test_board[1].shape, (9, 9))
            self.assertEqual(test_board[1].dtype, 'uint8')

        def test_make_one_hot(self):
            self.assertRaises(ValueError, lambda: make_one_hot(ref_board=None, num_clues=None))
            test_board_a = make_one_hot(num_clues=30)
            self.assertEqual(test_board_a.shape, (2, 9, 9, 9))
            self.assertEqual(test_board_a.dtype, 'bool')
            self.assertEqual(test_board_a[0].shape, (9, 9, 9))
            self.assertEqual(test_board_a[0].dtype, 'bool')
            self.assertEqual(test_board_a[1].shape, (9, 9, 9))
            self.assertEqual(test_board_a[1].dtype, 'bool')

            test_board_b = make_one_hot(ref_board=make_board(30))
            self.assertEqual(test_board_b.shape, (2, 9, 9, 9))
            self.assertEqual(test_board_b.dtype, 'bool')
            self.assertEqual(test_board_b[0].shape, (9, 9, 9))
            self.assertEqual(test_board_b[0].dtype, 'bool')
            self.assertEqual(test_board_b[1].shape, (9, 9, 9))
            self.assertEqual(test_board_b[1].dtype, 'bool')

        def test_make_boards(self):
            # TODO Add assertRaises TheoreticalLimit

            test_a = make_boards(10, 30, one_hot=False)
            self.assertEqual(test_a.shape, (10, 2, 9, 9))
            self.assertEqual(test_a.dtype, 'uint8')

            test_b = make_boards(10, 30, one_hot=True)
            self.assertEqual(test_b.shape, (10, 2, 9, 9, 9))
            self.assertEqual(test_b.dtype, 'bool')

        def test_name_dataset(self):
            self.assertEqual(name_dataset(10, [20, 30, 40, 50], True),
                             '10x[20,30,40,50]_one_hot')
            self.assertEqual(name_dataset(10, [20, 30, 40, 50], False),
                             '10x[20,30,40,50]_int')

        def test_make_dataset(self):
            # TODO More thorough testing
            self.assertTrue(make_dataset(10, 30, one_hot=False, name='test_data'))
            self.assertTrue(os.path.exists('test_data.h5f'))  # TODO Verify correct file extension
            if os.path.exists('test_data.h5f'):
                os.remove('test_data.h5f')

        def tearDown(self):
            pass


    unittest.main(verbosity=2)
