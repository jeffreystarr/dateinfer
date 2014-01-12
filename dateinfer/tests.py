import unittest
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
