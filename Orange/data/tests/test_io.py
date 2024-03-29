import unittest
import numpy as np

from Orange.data import ContinuousVariable, DiscreteVariable, StringVariable
from Orange.data.io import guess_data_type


class TestTableFilters(unittest.TestCase):

    def test_guess_data_type_continuous(self):
        # should be ContinuousVariable
        valuemap, values, coltype = guess_data_type(list(range(1, 100)))
        self.assertEqual(ContinuousVariable, coltype)
        self.assertIsNone(valuemap)
        np.testing.assert_array_equal(np.array(list(range(1, 100))), values)

        valuemap, values, coltype = guess_data_type([1, 2, 3, 1, 2, 3])
        self.assertEqual(ContinuousVariable, coltype)
        self.assertIsNone(valuemap)
        np.testing.assert_array_equal([1, 2, 3, 1, 2, 3], values)

        valuemap, values, coltype = guess_data_type(
            ["1", "2", "3", "1", "2", "3"])
        self.assertEqual(ContinuousVariable, coltype)
        self.assertIsNone(valuemap)
        np.testing.assert_array_equal([1, 2, 3, 1, 2, 3], values)

    def test_guess_data_type_discrete(self):
        # should be DiscreteVariable
        valuemap, values, coltype = guess_data_type([1, 2, 1, 2])
        self.assertEqual(DiscreteVariable, coltype)
        self.assertEqual([1, 2], valuemap)
        np.testing.assert_array_equal([1, 2, 1, 2], values)

        valuemap, values, coltype = guess_data_type(["1", "2", "1", "2", "a"])
        self.assertEqual(DiscreteVariable, coltype)
        self.assertEqual(["1", "2", "a"], valuemap)
        np.testing.assert_array_equal(['1', '2', '1', '2', 'a'], values)

        # just below the threshold for string variable
        in_values = list(map(lambda x: str(x) + "a", range(24))) + ["a"] * 76
        valuemap, values, coltype = guess_data_type(in_values)
        self.assertEqual(DiscreteVariable, coltype)
        self.assertEqual(sorted(set(in_values)), valuemap)
        np.testing.assert_array_equal(in_values, values)

    def test_guess_data_type_string(self):
        # should be StringVariable
        # too many different values for discrete
        in_values = list(map(lambda x: str(x) + "a", range(90)))
        valuemap, values, coltype = guess_data_type(in_values)
        self.assertEqual(StringVariable, coltype)
        self.assertIsNone(valuemap)
        np.testing.assert_array_equal(in_values, values)

        # more than len(values)**0.7
        in_values = list(map(lambda x: str(x) + "a", range(25))) + ["a"] * 75
        valuemap, values, coltype = guess_data_type(in_values)
        self.assertEqual(StringVariable, coltype)
        self.assertIsNone(valuemap)
        np.testing.assert_array_equal(in_values, values)

        # more than 100 different values - exactly 101
        # this is the case when len(values)**0.7 rule would vote for the
        # DiscreteVariable
        in_values = list(map(lambda x: str(x) + "a", range(100))) + ["a"] * 999
        valuemap, values, coltype = guess_data_type(in_values)
        self.assertEqual(StringVariable, coltype)
        self.assertIsNone(valuemap)
        np.testing.assert_array_equal(in_values, values)
