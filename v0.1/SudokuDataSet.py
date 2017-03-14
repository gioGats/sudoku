import numpy as np
from random import shuffle


class SudokuDataSet(object):
    def __init__(self, test_portion=0.15):
        self._train_x = self._train_y = self._test_x = self._test_y = None
        self.make_feature_sets(test_portion)
        # ISSUE Currently returns raw one-hot vectors.
        # Would like a class that can generate multiple types,
        # say numerical and one-hot for in-order and explicit-convolution.

        self._num_examples = len(self._train_x)
        self._epochs_completed = 0
        self._index_in_epoch = 0

    def make_feature_sets(self, test_portion):
        self.process_data()
        shuffle(examples)  # ISSUE examples is undefined

        testing_size = int(test_portion * len(examples))

        self._train_x = np.array(examples[:, 0][:-testing_size])
        self._train_y = np.array(examples[:, 1][:-testing_size])
        self._test_x = np.array(examples[:, 0][-testing_size:])
        self._test_y = np.array(examples[:, 1][-testing_size:])

    def process_data(self):
        examples = self.load_csv()
        one_hots = []
        test_total = len(examples)
        test_i = 0
        for ex in examples:
            new_line = []
            for item in ex:
                new_line.append(self.to_one_hot(item))
            one_hots.append(new_line)
            test_i += 1
            print('\rProgress: %.4f' % (test_i/test_total), end='')
        return one_hots

    @staticmethod
    def load_csv():
        examples = []
        for line in open('data/sudoku_copy.csv', 'r'):
            examples.append(line.replace('\n', '').split(","))
        return examples

    @staticmethod
    def to_one_hot(string):
        vector = []
        for char in string:
            add_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            add_vector[int(char)] = 1
            vector.append(add_vector)
        return np.array(vector)

    @staticmethod
    def to_string(one_hot):
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
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            perm = np.arange(self._num_examples)
            np.random.shuffle(perm)
            self._train_x = self._train_x[perm]
            self._train_y = self._train_y[perm]

            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples

        end = self._index_in_epoch
        return self._train_x[start:end], self._train_y[start:end]


if __name__ == '__main__':
    d = SudokuDataSet()
    print('Dataset loaded')
    print(d.next_batch(batch_size=1))
    import pickle
    pickle.dump(d, open('SDS_Dump.pkl', 'wb'))

