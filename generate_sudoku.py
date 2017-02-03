"""
Code Sources Used:
https://gist.github.com/mythz/5723202
https://github.com/dartist/sudoku_solver/blob/master/benchmarks/sudoku.py
https://github.com/gioGats/sudoku
http://norvig.com/sudoku.html
"""
import random


# API/Adapted Code #####################################################################################################

def generate_puzzles(num_puzzles, num_clues, output_filename):
    # TODO Generate num_puzzles with num_clues
    # TODO verify this works
    output = open(output_filename, 'w')
    for i in range(num_puzzles):
        output.write(generate_puzzle(num_clues, asTuple=False))
        output.write('\n')
    output.close()


def generate_puzzle(num_clues, asTuple=False):
    # TODO Generate a puzzle, solution tuple where the puzzle has num_clues
    # TODO if string, return as a string, example:
    #    '004300209005009001070060043006002087190007400050083000600000105003508690042910300,
    #     864371259325849761971265843436192587198657432257483916689734125713528694542916378'
    # TODO elif tuple, return as a tuple, example:
    #   ('004300209005009001070060043006002087190007400050083000600000105003508690042910300',
    #    '864371259325849761971265843436192587198657432257483916689734125713528694542916378')z
    #
    # TODO Must be a valid puzzle!
    # TODO Use of the below refence code is fine, but make sure it works in Python3 (it's currently in Python2)
    # TODO Make sure it works at the theoretical limit (num_clues -> 17)
    result = random_puzzle(num_clues)
    solution = solve(result)
    solution_string, solution_tuple = "", []

    for r in rows:
        solution_string += (''.join(solution[r + c] for c in cols))

    if asTuple:
        solution_tuple.extend((result, solution_string))
        return solution_tuple
    else:
        return result + ',\n' + solution_string


# Norvig's Code ########################################################################################################

def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [a + b for a in A for b in B]


digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits
squares = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s], [])) - {s})
             for s in squares)


# Parse a Grid #########################################################################################################

def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    # To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s, d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False  # (Fail if we can't assign d to square s.)
    return values


def grid_values(grid):
    """Convert grid into a dict of {square: char} with '0' or '.' for empties."""
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))


# Constraint Propagation ###############################################################################################

def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False


def eliminate(values, s, d):
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
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    # (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False  # Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values


# Display as 2-D grid ##################################################################################################

def display(values):
    """Display these values as a 2-D grid."""
    width = 1 + max(len(values[s]) for s in squares)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)


# Search ###############################################################################################################

def solve(grid): return search(parse_grid(grid))


def search(values):
    """Using depth-first search and propagation, try all possible values."""
    if values is False:
        return False  # Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values  # Solved!
    # Chose the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d))
                for d in values[s])


def some(seq):
    """Return some element of seq that is true."""
    for e in seq:
        if e: return e
    return False


# API Used #############################################################################################################

def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) == N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s]) == 1 else '0' for s in squares)
    return random_puzzle(N)  # Give up and make a new puzzle


def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq