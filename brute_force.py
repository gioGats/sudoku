import sys
import time


class ProgressStalled(Exception):
    pass


class Failure(Exception):
    pass


class Finished(Exception):
    pass


class Puzzle(object):
    def __init__(self, string=None):
        assert (isinstance(string, str) or isinstance(string, None))
        if string is None:
            raise NotImplementedError("Random generation not enabled")
        else:
            self.board = []
            for i in list(string):
                self.board.append(Cell(list(string).index(i), int(i)))
            self.rows = self.make_rows()
            self.columns = self.make_columns()
            self.squares = self.make_squares()

    def solve(self, non_definite=False):
        try:
            self.definite_fill()
        except ProgressStalled:
            pass
        except Finished:
            return
        if non_definite:
            try:
                self.non_definite_fill()
            except ProgressStalled:
                pass
            except Finished:
                return
            except Failure:
                pass
        else:
            raise Failure

    def definite_fill(self):
        while not self.is_finished():
            improve = 0
            for i in [self.rows, self.columns, self.squares]:
                for j in i:
                    current_actuals = []
                    for k in j:
                        # noinspection PyTypeChecker
                        cell = self.board[k]
                        current_actuals.append(cell.actual)
                    for k in j:
                        # noinspection PyTypeChecker
                        cell = self.board[k]
                        cell.remove_possible(current_actuals)
            for cell in self.board:
                if cell.check():
                    improve += 1
            if improve <= 0:
                raise ProgressStalled
        raise Finished

    def non_definite_fill(self):
        cells_remaining = []
        for cell in self.board:
            if cell.actual == 0:
                cells_remaining.append(cell)
        cells_remaining.sort()
        options = []
        for cell in cells_remaining:
            for option in cell.possible:
                options.append((cell.index, option))
        while not self.is_finished():
            choice = options.pop()
            new_puzzle = Puzzle(self.__repr__())
            new_puzzle.board[choice[0]].actual = choice[1]
            try:
                new_puzzle.solve(non_definite=False)
            except ProgressStalled:
                pass
            except Finished:
                self.board = new_puzzle.board
                raise Finished

        cells_remaining = []
        for cell in self.board:
            if cell.actual == 0:
                cells_remaining.append(cell)
        cells_remaining.sort()
        options = []
        for cell in cells_remaining:
            for option in cell.possible:
                options.append((cell.index, option))
        while not self.is_finished():
            choice = options.pop()
            new_puzzle = Puzzle(self.__repr__())
            new_puzzle.board[choice[0]].actual = choice[1]
            try:
                new_puzzle.solve(non_definite=True)
            except ProgressStalled:
                pass
            except Finished:
                self.board = new_puzzle.board
                raise Finished

    def is_finished(self):
        for cell in self.board:
            if cell.actual == 0:
                return False
        return True

    def failure(self):
        for cell in self.board:
            if cell.actual == 0 and len(cell.possible) == 0:
                return True
        return False

    @staticmethod
    def make_rows():
        all_rows = []
        for i in range(0, 8 + 1):
            this_row = []
            for x in range(0, 8 + 1):
                this_row.append(9 * i + x)
            all_rows.append(this_row)
        return all_rows

    @staticmethod
    def make_columns():
        all_columns = []
        for i in range(0, 8 + 1):
            this_column = []
            for x in range(0, 8 + 1):
                this_column.append(i + 9 * x)
            all_columns.append(this_column)
        return all_columns

    @staticmethod
    def make_squares():
        all_squares = []
        for i in [0, 3, 6, 27, 30, 33, 54, 57, 60]:
            this_square = []
            for x in [0, 1, 2, 9, 10, 11, 18, 19, 20]:
                this_square.append(i + x)
            all_squares.append(this_square)
        return all_squares

    def __str__(self):
        return_string = ''
        i = 1
        for cell in self.board:
            return_string += str(cell.actual)
            if i % 9 == 0:
                return_string += '\n'
            i += 1
        return return_string

    def __repr__(self):
        return_string = ''
        for cell in self.board:
            return_string += str(cell.actual)
        return return_string

    def __eq__(self, other):
        if isinstance(other, str):
            return self.__repr__() == other
        elif isinstance(other, Puzzle):
            return self.board == other.board


class Cell(object):
    def __init__(self, index, value=0):
        self.index = index
        if value == 0:
            self.possible = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            self.actual = 0
        else:
            self.possible = []
            self.actual = value

    def check(self):
        if self.actual == 0 and len(self.possible) == 1:
            self.actual = self.possible[0]
            return True
        else:
            return False

    def remove_possible(self, value):
        if isinstance(value, int):
            if value in self.possible:
                self.possible.remove(value)
        elif isinstance(value, list):
            for v in value:
                self.remove_possible(v)
        else:
            raise ValueError("Improper input type")

    def __eq__(self, other):
        return self.actual == other.actual

    def __gt__(self, other):
        return len(self.possible) > len(other.possible)

    def __lt__(self, other):
        return len(self.possible) < len(other.possible)


if __name__ == '__main__':
    try:
        num_examples = sys.argv[1]
    except IndexError:
        num_examples = 1000000  # Default
    print('Testing brute force, %d examples' % num_examples)
    # FUTURE Add random sampling from complete csv
    examples = []
    for line in open('data/sudoku_copy.csv', 'r'):
        examples.append(line.replace('\n', '').split(","))
    examples.reverse()
    global_start = time.time()
    trial = success = fail = 0
    try:
        for ex in examples:
            local_start = time.time()
            trial += 1
            start = ex[0]
            solution = ex[1]
            puzzle = Puzzle(start)
            print("\rTrial %d of %d:" % (trial, num_examples), end='')
            puzzle.solve(non_definite=True)
            local_end = time.time()
            if puzzle == solution:
                # #print(' success in %.10f seconds' % (local_end - local_start))
                success += 1
            else:
                # #print(' failure in %.10f seconds' % (local_end - local_start))
                fail += 1
        raise KeyboardInterrupt
    except KeyboardInterrupt:
        global_end = time.time()
        print('Testing complete in %.10f seconds' % (global_end - global_start))
        print('%d suceesses and %d failures in %d trials' % (success, fail, trial))
