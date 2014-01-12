import unittest
from dateinfer.date_elements import *
import infer
import yaml

def load_tests(loader, standard_tests, ignored):
    """
    Return a TestSuite containing standard_tests plus generated test cases
    """
    suite = unittest.TestSuite()
    suite.addTests(standard_tests)

    with open('examples.yaml', 'r') as f:
        examples = yaml.safe_load_all(f)
        for example in examples:
            suite.addTest(test_case_for_example(example))

    return suite

def test_case_for_example(test_data):
    """
    Return an instance of TestCase containing a test for a date-format example
    """

    # This class definition placed inside method to prevent discovery by test loader
    class TestExampleDate(unittest.TestCase):
        def testFormat(self):
            # verify initial conditions
            self.assertTrue(hasattr(self, 'test_data'), 'testdata field not set on test object')

            expected = self.test_data['format']
            actual = infer.infer(self.test_data['examples'])

            self.assertEqual(expected,
                             actual,
                             '{0}: Inferred `{1}`!=`{2}`'.format(self.test_data['name'], actual, expected))

    test_case = TestExampleDate(methodName='testFormat')
    test_case.test_data = test_data
    return test_case


class TestMode(unittest.TestCase):
    def testMode(self):
        self.assertEqual(5, infer._mode([1,3,4,5,6,5,2,5,3]))
        self.assertEqual(2, infer._mode([1,2,2,3,3]))  # with ties, pick least value


class TestMostRestrictive(unittest.TestCase):
    def testMostRestrictive(self):
        t = infer._most_restrictive

        self.assertEqual(MonthNum(), t([DayOfMonth(), MonthNum, Year4()]))
        self.assertEqual(Year2(), t([Year4(), Year2()]))


class TestPercentMatch(unittest.TestCase):
    def testPercentMatch(self):
        t = infer._percent_match
        patterns = (DayOfMonth, MonthNum, Filler)
        examples = ['1', '2', '24', 'b', 'c']

        percentages = t(patterns, examples)

        self.assertAlmostEqual(percentages[0], 0.6)  # DayOfMonth 1..31
        self.assertAlmostEqual(percentages[1], 0.4)  # Month 1..12
        self.assertAlmostEqual(percentages[2], 1.0)  # Filler any


class TestTagMostLikely(unittest.TestCase):
    def testTagMostLikely(self):
        examples = ['8/12/2004', '8/14/2004', '8/16/2004']
        t = infer._tag_most_likely

        actual = t(examples)
        expected = [MonthNum(), Filler('/'), DayOfMonth(), Filler('/'), Year4()]

        self.assertListEqual(actual, expected)


class TestTokenizeByCharacterClass(unittest.TestCase):
    def testTokenize(self):
        t = infer._tokenize_by_character_class

        self.assertListEqual([], t(''))
        self.assertListEqual(['2013', '-', '08', '-', '14'], t('2013-08-14'))
        self.assertListEqual(['Sat', ' ', 'Jan', ' ', '11', ' ', '19', ':', '54', ':', '52', ' ', 'MST', ' ', '2014'],
                             t('Sat Jan 11 19:54:52 MST 2014'))
        self.assertListEqual(['4', '/', '30', '/', '1998', ' ', '4', ':', '52', ' ', 'am'], t('4/30/1998 4:52 am'))
