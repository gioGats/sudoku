import sys
import time


class Puzzle(object):
    def __init__(self, string=None):
        assert (isinstance(string, str) or isinstance(string, None))
        if string is None:
            raise NotImplementedError("Random generation not enabled")
        else:
            self.board = []
            for i in list(string):
                self.board.append(Cell(int(i)))
            self.rows = self.make_rows()
            self.columns = self.make_columns()
            self.squares = self.make_squares()

    def solve(self):
        while not self.is_finished():
            if not self.iterate():
                break
            # #print(self)

    def iterate(self):
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
                    # FUTURE deal with potential hang
        for cell in self.board:
            if cell.check():
                improve += 1
        if improve > 0:
            return True
        else:
            return False

    def is_finished(self):
        for i in self.board:
            if i.actual is None or i.actual == 0:
                return False
        return True

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
    def __init__(self, value=0):
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
    global_start = time.time()
    trial = 1
    success = fail = 0
    for ex in examples:
        local_start = time.time()
        start = ex[0]
        solution = ex[1]
        puzzle = Puzzle(start)
        print("Trial %d of %d:" % (trial, num_examples), end='')
        puzzle.solve()
        local_end = time.time()
        if puzzle == solution:
            print(' success in %.10f seconds' % (local_end - local_start))
            success += 1
        else:
            print(' failure in %.10f seconds' % (local_end - local_start))
            fail += 1
        trial += 1
    global_end = time.time()
    print('Testing complete in %.10f seconds' % (global_end - global_start))
    print('%d suceesses and %d failures' % (success, fail))
