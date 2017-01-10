import numpy as np


def to_one_hot(string):
    vector = []
    for char in string:
        add_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        add_vector[int(char)] = 1
        vector += add_vector
    return np.array(vector)


def to_string(one_hot):
    string = ''
    for row in one_hot.reshape(-1, 10):
        string += str(list(row).index(1))
    return string

if __name__ == '__main__':
    s = '004300209005009001070060043006002087190007400050083000600000105003508690042910300'
    o = to_one_hot(s)
    print(o)
    print(s)
    print(to_string(o))