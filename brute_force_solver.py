import numpy as np
import unittest

from sudoku_generator import *


def brute_force_solve(board):
    """
    Solves a given board
    :raises ValueError if board shape or dtype incorrect
    :param board: np.ndarray of puzzle board, shape=(9,9) dtype='uint8' OR shape=(9,9,9) dtype='bool'
    :return: np.ndarray of solved board, same shape and dtype as param board.
    """
    if board.shape == (9, 9, 9) and board.dtype == 'bool':
        categories = [[False, False, False, False, False, False, False, False, False],
                      [True, False, False, False, False, False, False, False, False],
                      [False, True, False, False, False, False, False, False, False],
                      [False, False, True, False, False, False, False, False, False],
                      [False, False, False, True, False, False, False, False, False],
                      [False, False, False, False, True, False, False, False, False],
                      [False, False, False, False, False, True, False, False, False],
                      [False, False, False, False, False, False, True, False, False],
                      [False, False, False, False, False, False, False, True, False],
                      [False, False, False, False, False, False, False, False, True]]

        board_string = ''
        for x in range(0, len(board)):
            for y in range(0, len(board[0])):
                for i in range(0, len(categories)):
                    if np.array_equal(board[x][y], categories[i]):
                        board_string += str(i)

        rows = 'ABCDEFGHI'
        cols = '123456789'

        # Assume solvable
        solution_dict = solve(board_string)

        solution_string = ""

        for r in rows:
            solution_string += (''.join(solution_dict[r + c] for c in cols))

        solution_uint = np.fromstring(solution_string, dtype='uint8').reshape(9, 9)
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

        s = []
        for x in range(0, len(solution_uint)):
            for y in range(0, len(solution_uint[x])):
                if solution_uint[x][y] in onehots:
                    s.append(onehots[solution_uint[x][y]])

        s = [s[i:i + 9] for i in range(0, len(s), 9)]
        bool_solution = np.array(s, dtype=np.bool)

        return bool_solution

    elif board.shape == (9, 9) and board.dtype == 'uint8':
        categories = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]

        board_string = ''
        for x in range(0, len(board)):
            for y in range(0, len(board[0])):
                for i in range(0, len(categories)):
                    if np.array_equal(board[x][y], categories[i]):
                        board_string += str(i)

        rows = 'ABCDEFGHI'
        cols = '123456789'

        # Assume solvable
        solution_dict = solve(board_string)

        solution_string = ""

        for r in rows:
            solution_string += (''.join(solution_dict[r + c] for c in cols))

        solution_uint = np.fromstring(solution_string, dtype='uint8').reshape(9, 9)
        return solution_uint
    else:
        raise ValueError('Incorrect board formatting')


class TestBruteForceSolver(unittest.TestCase):
    def setUp(self):
        pass

    def test_brute_force_solve(self):
        self.assertRaises(ValueError, lambda: brute_force_solve(np.array([])))
        from make_data import make_board, make_one_hot

        test_board_int = make_board(50)

        test_result_int = brute_force_solve(test_board_int[0])
        self.assertEqual(test_result_int.shape, (9, 9))
        self.assertEqual(test_result_int.dtype, 'uint8')
        np.testing.assert_array_equal(test_result_int, test_board_int[1])

        test_board_one_hot = make_one_hot(ref_board=test_board_int)
        test_result_one_hot = brute_force_solve(test_board_one_hot[0])
        self.assertEqual(test_result_one_hot.shape, (9, 9, 9))
        self.assertEqual(test_result_one_hot.dtype, 'bool')
        np.testing.assert_array_equal(test_result_one_hot, test_board_one_hot[1])

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
