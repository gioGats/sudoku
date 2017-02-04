"""
Code Sources Used:
https://github.com/gioGats/sudoku
http://norvig.com/sudoku.html
"""

import itertools
import sys
import time

import generate_sudoku as gs


# TODO Rewrite definite_fill and indefinite_fill into new functions: update_possible, fill_definite, indefinite_fill
# TODO modify indefinite_fill.  BFS testing each node with update_possible+fill_definite combo.

class Puzzle(object):
    def __init__(self, string=None):
        assert (isinstance(string, str) or isinstance(string, None))
        if string is None:
            raise NotImplementedError("Random generation not enabled")
        else:
            self.cell_values = gs.grid_values(string)
            self.digits = '123456789'
            self.rows = 'ABCDEFGHI'
            self.cols = self.digits
            self.puzzle_string = ''

    def solve(self):
        editable_ids = []
        for cell_id in self.cell_values:
            if self.cell_values[cell_id] is '0':
                editable_ids.append(cell_id)

        brute_dict = self.get_possible_values(editable_ids)
        brute_list = []
        brute_list_ids = []
        for value in brute_dict.keys():
            brute_list_ids.append(str(value))
            brute_list.append(list(brute_dict[str(value)]))

        for i in range(0, 1000000000, 1000):
            if self.brute_gen(brute_list, brute_list_ids, start=0 + i, end=1000 + i):
                results = self.cell_values
                for r in self.rows:
                    self.puzzle_string += (''.join(results[r + c] for c in self.cols))
                gs.display(self.cell_values)
                print('///////////////////')
                return self.puzzle_string

        print('Options Exhausted')
        print('///////////////////')

    def get_possible_values(self, values):
        values_dict = {}
        for i in range(0, len(values), 1):
            possible_values = set()
            for value in list(self.valid_fill(values[i])):
                possible_values.add(str(value))
            else:
                values_dict[str(values[i])] = possible_values
        return values_dict

    def brute_gen(self, brute_list, brute_list_ids, start, end):
        brute_gen1000 = list(itertools.islice(itertools.product(*brute_list), start, end, 1))
        for sequence in brute_gen1000:
            send_sequence = list(sequence)
            valid_result = self.brute_fill(brute_list_ids, send_sequence)
            if valid_result:
                return True
            else:
                for rollback_id in brute_list_ids:
                    self.cell_values[rollback_id] = '0'

# Keith's WIP Zone: UNDER CONSTRUCTION #################################################################################

    '''
    def help_brute_fill(self, cell_id, possible_values):
        possible_values = list(possible_values)
        for i in range(0, len(possible_values), 1):
            if self.is_valid(cell_id, possible_values[i]):
                self.self.cell_values[cell_id] = possible_values[i]
                return 'Set' '''

    def valid_fill(self, cell_id):
        possible_numbers = list(range(1, 10))
        # ISSUE: This loop is very brash. It works, but it could work better.
        # noinspection PyUnusedLocal
        for n in list(range(3)):
            for number in possible_numbers:
                if str(number) in (self.cell_values[cell_id2] for cell_id2 in gs.units[cell_id][0]):
                    possible_numbers.remove(number)
                elif str(number) in (self.cell_values[cell_id2] for cell_id2 in gs.units[cell_id][1]):
                    possible_numbers.remove(number)
                elif str(number) in (self.cell_values[cell_id2] for cell_id2 in gs.units[cell_id][2]):
                    possible_numbers.remove(number)
        return ''.join(map(str, possible_numbers))

    def brute_fill(self, cell_ids, cell_values):
        for i in range(0, len(cell_ids), 1):
            self.cell_values[cell_ids[i]] = str(cell_values[i])

        for i in range(0, len(cell_ids), 1):
            if self.is_valid(cell_ids[i], cell_values[i]):
                return True
            else:
                return False

    def is_valid(self, cell_id, cell_value):
        peer_cols = gs.units[cell_id][0]
        peer_rows = gs.units[cell_id][1]
        peer_boxs = gs.units[cell_id][2]
        peer_cols.remove(cell_id)
        peer_rows.remove(cell_id)
        peer_boxs.remove(cell_id)
        # input('?')
        for cell_id2 in peer_cols:
            if self.cell_values[cell_id] == self.cell_values[cell_id2]:
                peer_cols.append(cell_id)
                peer_rows.append(cell_id)
                peer_boxs.append(cell_id)
                return False
        for cell_id2 in peer_rows:
            if self.cell_values[cell_id] == self.cell_values[cell_id2]:
                peer_cols.append(cell_id)
                peer_rows.append(cell_id)
                peer_boxs.append(cell_id)
                return False
        for cell_id2 in peer_boxs:
            if self.cell_values[cell_id] == self.cell_values[cell_id2]:
                peer_cols.append(cell_id)
                peer_rows.append(cell_id)
                peer_boxs.append(cell_id)
                return False
        peer_cols.append(cell_id)
        peer_rows.append(cell_id)
        peer_boxs.append(cell_id)
        return True


# UNDER CONSTRUCTION ###################################################################################################

if __name__ == '__main__':
    f = open('failures.txt', 'w')
    try:
        num_examples = sys.argv[1]
    except IndexError:
        num_examples = 100  # Default

    # Effective Range: 17-77
    print('Generating...')
    gs.generate_puzzles(1, 55, 'data/sudoku.txt')

    print('Testing brute force, %d examples' % num_examples)
    # FUTURE Add random sampling from complete csv
    examples = []
    sf = open('data/sudoku.txt', 'r').read().replace(',', '').splitlines()
    for i in range(0, len(sf), 2):
        examples.append([sf[i], sf[i + 1]])
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
            print("Trial %d of %d:\n" % (trial, num_examples))
            puzzle = puzzle.solve()
            local_end = time.time()
            if puzzle == solution:
                print(' success in %.10f seconds' % (local_end - local_start))
                success += 1
            else:
                print(' failure in %.10f seconds' % (local_end - local_start))
                # f.write(puzzle.__repr__() + '\n')
                fail += 1
        raise KeyboardInterrupt
    except KeyboardInterrupt:
        global_end = time.time()
        print('Testing complete in %.10f seconds' % (global_end - global_start))
        print('%d suceesses and %d failures in %d trials' % (success, fail, trial))
        f.close()
