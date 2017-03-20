import os
import re

import random
import numpy as np


class TheoreticalLimit(Exception):
    pass


# Class below's code courtesy of Peter Norvig at http://norvig.com/sudoku.html
class NorvigCode(object):
    def __init__(self):
        self.digits = '123456789'
        self.rows = 'ABCDEFGHI'
        self.cols = self.digits
        self.squares = self.cross(self.rows, self.cols)
        self.unitlist = ([self.cross(self.rows, c) for c in self.cols] +
                    [self.cross(r, self.cols) for r in self.rows] +
                    [self.cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])
        self.units = dict((s, [u for u in self.unitlist if s in u])
                     for s in self.squares)
        self.peers = dict((s, set(sum(self.units[s], [])) - {s})
                     for s in self.squares)

    def cross(self, A, B):
        """Cross product of elements in A and elements in B."""
        return [a + b for a in A for b in B]

    def shuffled(self, seq):
        """Return a randomly shuffled copy of the input sequence."""
        seq = list(seq)
        random.shuffle(seq)
        return seq

    def parse_grid(self, grid):
        """Convert grid to a dict of possible values, {square: digits}, or
        return False if a contradiction is detected."""
        # To start, every square can be any digit; then assign values from the grid.
        values = dict((s, self.digits) for s in self.squares)
        for s, d in self.grid_values(grid).items():
            if d in self.digits and not self.assign(values, s, d):
                return False  # (Fail if we can't assign d to square s.)
        return values

    def grid_values(self, grid):
        """Convert grid into a dict of {square: char} with '0' or '.' for empties."""
        chars = [c for c in grid if c in self.digits or c in '0.']
        assert len(chars) == 81
        return dict(zip(self.squares, chars))

    def assign(self, values, s, d):
        """Eliminate all the other values (except d) from values[s] and propagate.
        Return values, except return False if a contradiction is detected."""
        other_values = values[s].replace(d, '')
        if all(self.eliminate(values, s, d2) for d2 in other_values):
            return values
        else:
            return False

    def eliminate(self, values, s, d):
        """Eliminate d from values[s]; propagate when values or places <= 2.
        Return values, except return False if a contradiction is detected."""
        if d not in values[s]:
            return values  # Already eliminated
        values[s] = values[s].replace(d, '')
        # (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
        if len(values[s]) == 0:
            return False  # Contradiction: removed last value
        elif len(values[s]) == 1:
            d2 = values[s]
            if not all(self.eliminate(values, s2, d2) for s2 in self.peers[s]):
                return False
        # (2) If a unit u is reduced to only one place for a value d, then put it there.
        for u in self.units[s]:
            dplaces = [s for s in u if d in values[s]]
            if len(dplaces) == 0:
                return False  # Contradiction: no place for this value
            elif len(dplaces) == 1:
                # d can only be in one place in unit; assign it there
                if not self.assign(values, dplaces[0], d):
                    return False
        return values

    def solve(self, grid):
        return self.search(self.parse_grid(grid))

    def search(self, values):
        """Using depth-first search and propagation, try all possible values."""
        if values is False:
            return False  # Failed earlier
        if all(len(values[s]) == 1 for s in self.squares):
            return values  # Solved!
        # Chose the unfilled square s with the fewest possibilities
        n, s = min((len(values[s]), s) for s in self.squares if len(values[s]) > 1)
        return self.some(self.search(self.assign(values.copy(), s, d))
                    for d in values[s])

    def some(self, seq):
        """Return some element of seq that is true."""
        for e in seq:
            if e: return e
        return False

    def random_puzzle(self, N=17):
        """Make a random puzzle with N or more assignments. Restart on contradictions.
        Note the resulting puzzle is not guaranteed to be solvable, but empirically
        about 99.8% of them are solvable. Some have multiple solutions."""
        values = dict((s, self.digits) for s in self.squares)
        for s in self.shuffled(self.squares):
            if not self.assign(values, s, random.choice(values[s])):
                break
            ds = [values[s] for s in self.squares if len(values[s]) == 1]
            if len(ds) == N and len(set(ds)) >= 8:
                return ''.join(values[s] if len(values[s]) == 1 else '0' for s in self.squares)
        return self.random_puzzle(N)  # Give up and make a new puzzle


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
    solution_string = ""

    for r in rows:
        solution_string += (''.join(solution_dict[r + c] for c in cols))

    board_grid = np.fromstring(board_string, dtype='uint8').reshape(9, 9)
    solution_grid = np.fromstring(solution_string, dtype='uint8').reshape(9, 9)

    return np.array([board_grid, solution_grid], dtype='uint8')


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
    raise NotImplementedError


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
    raise NotImplementedError


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
            try:
                self.assertRaises(TheoreticalLimit, make_board(16))
            except TheoreticalLimit:
                pass
            test_board = make_board(30)
            self.assertEqual(test_board.shape, (2,9,9))
            self.assertEqual(test_board.dtype, 'uint8')
            self.assertEqual(test_board[0].shape, (9, 9))
            self.assertEqual(test_board[0].dtype, 'uint8')
            self.assertEqual(test_board[1].shape, (9, 9))
            self.assertEqual(test_board[1].dtype, 'uint8')

        def test_make_one_hot(self):
            self.assertRaises(ValueError, make_one_hot(ref_board=None, num_clues=None))
            test_board_a = make_one_hot(num_clues=30)
            self.assertEqual(test_board_a.shape, (2,9,9,9))
            self.assertEqual(test_board_a.dtype, 'bool')
            self.assertEqual(test_board_a[0].shape, (9, 9, 9))
            self.assertEqual(test_board_a[0].dtype, 'bool')
            self.assertEqual(test_board_a[1].shape, (9, 9, 9))
            self.assertEqual(test_board_a[1].dtype, 'bool')

            test_board_b = make_one_hot(ref_board=make_board(30))
            self.assertEqual(test_board_b.shape, (2,))
            self.assertEqual(test_board_b.dtype, 'bool')
            self.assertEqual(test_board_b[0].shape, (9, 9, 9))
            self.assertEqual(test_board_b[0].dtype, 'bool')
            self.assertEqual(test_board_b[1].shape, (9, 9, 9))
            self.assertEqual(test_board_b[1].dtype, 'bool')

        def test_make_boards(self):
            # TODO Add assertRaises TheoreticalLimit

            test_a = make_boards(10, 30, one_hot=False)
            self.assertEqual(test_a.shape, (10, 2))
            self.assertEqual(test_a.dtype, 'uint8')

            test_b = make_boards(10, 30, one_hot=True)
            self.assertEqual(test_b.shape, (10, 2))
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
