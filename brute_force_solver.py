import numpy as np


def brute_force_solve(board):
    """
    Solves a given board
    :raises ValueError if board shape or dtype incorrect
    :param board: np.ndarray of puzzle board, shape=(9,9) dtype='uint8' OR shape=(9,9,9) dtype='bool'
    :return: np.ndarray of solved board, same shape and dtype as param board.
    """
    if board.shape == (9, 9, 9) and board.dtype == 'bool':
        raise NotImplementedError
    elif board.shape == (9, 9) and board.dtype == 'uint8':
        raise NotImplementedError
    else:
        raise ValueError('Incorrect board formatting')

if __name__ == '__main__':
    import unittest

    class TestBruteForceSolver(unittest.TestCase):
        def setUp(self):
            pass

        def test_brute_force_solve(self):
            self.assertRaises(ValueError, brute_force_solve(np.array([])))
            from make_data import make_board, make_one_hot  # TODO Update import statements in actual repo

            test_board_int = make_board(40)
            test_result_int = brute_force_solve(test_board[0])
            self.assertEqual(test_result_int.shape, (9, 9))
            self.assertEqual(test_result_int.dtype, 'uint8')
            self.assertEqual(test_result_int, test_board_int[1])

            test_board_one_hot = make_one_hot(ref_board=test_board)
            test_result_one_hot = brute_force_solve(test_board_one_hot[0])
            self.assertEqual(test_result_one_hot.shape, (9, 9, 9))
            self.assertEqual(test_result_one_hot.dtype, 'bool')
            self.assertEqual(test_result_one_hot, test_board_one_hot[1])

        def tearDown(self):
            pass

    unittest.main(verbosity=2)
