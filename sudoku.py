#!/usr/bin/env python3

import argparse
import datetime

from make_data import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Sudoku Generator in Python by Keith Fernandez and Ryan Giarusso.', )

    parser.add_argument('-b', '--boards', help="Specifies how many boards are to be generated.", action="store",
                        nargs=1, required=False)

    parser.add_argument('-c', '--clues',
                        help="Specifies how many clues per board are to be generated. Supports multiple arguments.",
                        action="append", nargs='+', required=True)

    parser.add_argument('-o', '--one_hot',
                        help="Specifies that program should generate in one_hot bool format instead of uint8 format.",
                        action="store_true")

    parser.add_argument('-n', '--name',
                        help="Specifies what name the resulting HDF5 file will have.",
                        action="store", nargs=1)

    parser.add_argument('-d', '--destination',
                        help="Specifies what directory the resulting HDF5 file will be in.",
                        action="store", nargs=1)

    parser.add_argument('-sS', '--single_solution',
                        help="Specifies that boards will have one unique solution. WARNING: "
                             "Boards with single solutions and low numbers of clues will take much longer to generate!",
                        action="store_true")

    parser.add_argument('-iS', '--include_solutions',
                        help="Specifies that solution boards will be included in the resulting HDF5 file.",
                        action="store_true")

    # gen_parser.add_argument('-S')

    args = parser.parse_args()

    print('==================================================')
    print("=   Giarusso/Fernandez/Norvig Sudoku Generator   =")
    print('==================================================')

    start_time = datetime.datetime.now()
    make_dataset(num_boards=args.boards, clues_enum=args.clues, one_hot=args.one_hot, name=args.name,
                 dest=args.destination, single_solution=args.single_solution, include_solutions=args.include_solutions)

    end_time = datetime.datetime.now() - start_time
    print('\nFinished in ' + str(end_time) + ' seconds.')
