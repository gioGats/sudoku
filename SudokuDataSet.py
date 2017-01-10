import numpy as np
import tensorflow as tf


class SudokuDataSet(object):
    def __index__(self, ):
        pass

    def __init__(self, test_portion=0.5):
        self._train_x = self._train_y = self._test_x = self._test_y = None
        self.make_feature_sets(test_portion)

        self._num_examples = len(self._train_x)
        self._epochs_completed = 0
        self._index_in_epoch = 0

    def make_feature_sets(self, test_portion):
        pass

    def load_csv(self):
        pass

    def process_data(self):
        pass

    def to_one_hot(self, string):
        vector = []
        for char in string:
            add_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            add_vector[int(char)] = 1
            vector += add_vector
        return np.array(vector)

    def to_string(self, one_hot):
        string = ''
        for row in one_hot.reshape(-1, 10):
            string += str(list(row).index(1))
        return string

    @property
    def train_x(self):
        return self._train_x

    @property
    def train_y(self):
        return self._train_y

    @property
    def test_x(self):
        return self._test_x

    @property
    def test_y(self):
        return self._test_y

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size):
        pass


if __name__ == '__main__':
    d = SudokuDataSet()
    s = '004300209005009001070060043006002087190007400050083000600000105003508690042910300'
    o = d.to_one_hot(s)
    print(o)
    print(s)
    print(d.to_string(o))
