import numpy as np
import os
os.chdir('data')

DEBUG = False
PROGRESS = True
make_num_conv = True
make_onehot_order = True
make_onehot_conv = True


def convolute_board(board):
    all_rows = []
    for i in range(0, 8 + 1):
        this_row = []
        for x in range(0, 8 + 1):
            this_row.append(9 * i + x)
        all_rows.append(this_row)

    all_columns = []
    for i in range(0, 8 + 1):
        this_column = []
        for x in range(0, 8 + 1):
            this_column.append(i + 9 * x)
        all_columns.append(this_column)

    all_squares = []
    for i in [0, 3, 6, 27, 30, 33, 54, 57, 60]:
        this_square = []
        for x in [0, 1, 2, 9, 10, 11, 18, 19, 20]:
            this_square.append(i + x)
        all_squares.append(this_square)

    indicies = all_rows + all_columns + all_squares
    a = np.array(indicies)
    a = np.reshape(a, 243)

    conv_board = ''

    for i in a:
        conv_board += board[i]
    return conv_board


def onehot_seq(seq):
    new_seq = ''
    for char in seq:
        value = int(char)
        l = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        if value != 0:
            l[value-1] = 1
        onehot_char = ''
        for v in l:
            onehot_char += str(v)
        new_seq += onehot_char
    return new_seq


def num_conv(raw):
    new_file = open('num_conv.csv', 'w')
    count = 0
    total = len(raw)
    for row in raw:
        if row == '':
            continue
        row = row.replace('\n', '')
        i = row.split(',')
        new_file.write('%s,%s\n' % (convolute_board(i[0]), convolute_board(i[1])))
        if PROGRESS:
            print('\rNumber convolution: %.2f' % (100 * (count/total)), end='')
        count += 1
    new_file.close()
    if PROGRESS:
        print()


def onehot_order(raw):
    new_file = open('onehot_order.csv', 'w')
    count = 0
    total = len(raw)
    for row in raw:
        if row == '':
            continue
        row = row.replace('\n', '')
        i = row.split(',')
        x = onehot_seq(i[0])
        y = onehot_seq(i[1])
        new_file.write('%s,%s\n' % (x, y))
        if PROGRESS:
            print('\rOne-hot in-order: %.2f' % (100 * (count/total)), end='')
        count += 1
    new_file.close()
    if PROGRESS:
        print()


def onehot_conv(raw):
    new_file = open('onehot_conv.csv', 'w')
    count = 0
    total = len(raw)
    for row in raw:
        if row == '':
            continue
        row = row.replace('\n', '')
        i = row.split(',')
        x = onehot_seq(convolute_board(i[0]))
        y = onehot_seq(convolute_board(i[1]))
        new_file.write('%s,%s\n' % (x, y))
        if PROGRESS:
            print('\rOne-hot convolution: %.2f' % (100 * (count/total)), end='')
        count += 1
    new_file.close()
    if PROGRESS:
        print()


if __name__ == '__main__':
    if DEBUG:
        source_data = 'test_set.csv'
    else:
        source_data = 'num_order.csv'
    source_file = open(source_data, 'r')
    num_order = source_file.read().split('\n')
    if make_num_conv:
        num_conv(num_order)
    if make_onehot_order:
        onehot_order(num_order)
    if make_onehot_conv:
        onehot_conv(num_order)
    source_file.close()
