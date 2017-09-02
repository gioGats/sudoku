#!/usr/bin/env python3

import unittest
import sys


def userfile(unittests, filepath='tests.out'):
    with open(filepath, 'w+') as f:
        unittest.TextTestRunner(f).run(unittests)


def log(unittests):
    with open('tests.log', 'w+') as f:
        unittest.TextTestRunner(f).run(unittests)


def stdout(unittests):
    unittest.TextTestRunner(verbosity=2).run(unittests)


if __name__ == '__main__':
    DEFAULT_REPORTING = stdout
    # all options: stdout, log, userfile

    tests = unittest.defaultTestLoader.discover('.', pattern='*.py')

    if '-h' in sys.argv:
        print('Userfile: -t <userfile>\nLogfile: -l\nStdout: -s\nDefault: %s' % DEFAULT_REPORTING.__name__)
    elif '-t' in sys.argv:
        userfile(tests, sys.argv[sys.argv.index('-t') + 1])
    elif '-l' in sys.argv:
        log(tests)
    elif '-s' in sys.argv:
        stdout(tests)
    else:
        DEFAULT_REPORTING(tests)


