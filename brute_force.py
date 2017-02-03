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
            self.input_values = gs.grid_values(string)

            self.TEMP_input_values = gs.parse_grid(string)

            self.cell_values = list(self.input_values.keys())

            self.editable_values = []
            self.zeroes = 0

            #gs.display(self.input_values)
            #print('///////////////////')
            #gs.display(self.TEMP_input_values)
            #print('///////////////////')

            # print(gs.units['A1'])
            # print(gs.peers['A1'])

    '''
    first (P): generate a first candidate solution for P.
    next (P, c): generate the next candidate for P after the current one c.
    valid (P, c): check whether candidate c is a solution for P.
    output (P, c): use the solution c of P as appropriate to the application.

    c ← first(P)
    while c ≠ Λ do
     if valid(P,c) then output(P, c)
     c ← next(P,c)
    end while
    '''

    def solve(self):
        # while '0' in (self.input_values[all_values] for all_values in self.cell_values):
        for cell_id in self.cell_values:
            if self.input_values[cell_id] is '0':
                self.zeroes += 1
                self.editable_values.append(cell_id)

        brute_dict = self.get_possible_values()

        while self.zeroes > 14:
            for i in range(0, len(self.editable_values), 1):
                if self.help_brute_fill(self.editable_values[i], brute_dict[self.editable_values[i]]) is 'Set':
                    self.zeroes -= 1
                    # print(self.zeroes)
                if not self.zeroes > 14:
                    break

        brute_dict = self.get_possible_values()

        brute_list = []
        brute_list_ids = []
        for i in range(0, len(self.editable_values), 1):
            brute_list_ids.append(str(self.editable_values[i]))
            brute_list.append(list(brute_dict[str(self.editable_values[i])]))

        # print(brute_list_ids)
        # print(brute_list)

        for i in range(0, 1000000000, 10000):
            if self.brute_gen(i, brute_list, brute_list_ids) is 'Done':
                digits = '123456789'
                rows = 'ABCDEFGHI'
                cols = digits
                puzzle_string = ''
                for r in rows:
                    puzzle_string += (''.join(self.input_values[r + c] for c in cols))
                return puzzle_string

        print('Failed.')

    def get_possible_values(self):
        brute_dict = {}
        for i in range(0, len(self.editable_values), 1):
            possible_values = set()
            for value in list(self.valid_fill(self.editable_values[i])):
                possible_values.add(str(value))
            else:
                brute_dict[str(self.editable_values[i])] = possible_values
        return brute_dict

    def brute_gen(self, start, brute_list, brute_list_ids):
        brute_gen1000 = list(itertools.islice(itertools.product(*brute_list), start, start + 10000))

        for sequence in brute_gen1000:
            valid_result = self.brute_fill(brute_list_ids, sequence)
            if valid_result is 'Valid':
                return 'Done'
            if valid_result is 'Invalid':
                for cell_id in self.editable_values:
                    self.input_values[cell_id] = 0

# Keith's WIP Zone: UNDER CONSTRUCTION #################################################################################

    def help_brute_fill(self, cell_id, possible_values):
        possible_values = list(possible_values)
        for i in range(0, len(possible_values), 1):
            if self.is_valid(cell_id, possible_values[i]):
                self.input_values[cell_id] = possible_values[i]
                return 'Set'

    def valid_fill(self, cell_id):
        possible_numbers = list(range(1, 10))
        # ISSUE: This loop is very brash. It works, but it could work better.
        # noinspection PyUnusedLocal
        for n in list(range(3)):
            for number in possible_numbers:
                if str(number) in (self.input_values[cell_id2] for cell_id2 in gs.units[cell_id][0]):
                    possible_numbers.remove(number)
                elif str(number) in (self.input_values[cell_id2] for cell_id2 in gs.units[cell_id][1]):
                    possible_numbers.remove(number)
                elif str(number) in (self.input_values[cell_id2] for cell_id2 in gs.units[cell_id][2]):
                    possible_numbers.remove(number)
        return ''.join(map(str, possible_numbers))

    def brute_fill(self, cell_ids, numbers):
        for i in range(0, len(cell_ids), 1):
            if self.is_valid(cell_ids[i], numbers[i]):
                self.input_values[cell_ids[i]] = numbers[i]
            else:
                return 'Invalid'
        return 'Valid'

    def is_valid(self, cell_id, number):
        if str(number) not in (self.input_values[cell_id2] for cell_id2 in gs.units[cell_id][0]):
            if str(number) not in (self.input_values[cell_id2] for cell_id2 in gs.units[cell_id][1]):
                if str(number) not in (self.input_values[cell_id2] for cell_id2 in gs.units[cell_id][2]):
                    return True
        return False


# UNDER CONSTRUCTION ###################################################################################################

if __name__ == '__main__':
    f = open('failures.txt', 'w')
    try:
        num_examples = sys.argv[1]
    except IndexError:
        num_examples = 100  # Default

    #Effective Range: 17-77
    print('Generating...')
    gs.generate_puzzles(10, 60, 'data/sudoku.txt')

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
            print("\rTrial %d of %d:" % (trial, num_examples), end='')
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
