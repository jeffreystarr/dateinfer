"""Unit tests for dateinfer package"""
import os
import yaml

import pytest

from dateinfer.date_elements import (
    MonthNum, DayOfMonth, Year2, Year4,
    Filler, Hour12, Hour24,
    WeekdayShort, MonthTextShort,
    Minute, Second, Timezone,
)
from dateinfer.core import DateInfer
from dateinfer import ruleproc


EXAMPLES_FILENAME = os.path.join(os.path.abspath(os.path.dirname(__file__)), "examples.yaml")


@pytest.fixture(scope="module")
def test_data():
    with open(EXAMPLES_FILENAME, 'r') as f:
        examples = list(yaml.safe_load_all(f))

    return examples


def test_happy_path_on_examples(test_data):
    """Happy path on a set of designed examples"""
    for data in test_data:
        expected = data['format']
        actual = DateInfer.infer(data['examples'])

        assert expected == actual, '{0}: Inferred `{1}`!=`{2}`'.format(
            data['name'], actual, expected)


def test_ambiguous_date_cases():
    """Tests which results are ambiguous but can be assumed
    to fall in a small set of possibilities."""
    assert DateInfer.infer(['1/1/2012']) in ['%m/%d/%Y', '%d/%m/%Y']

    # Note: as described in Issue #5 (https://github.com/jeffreystarr/dateinfer/issues/5),
    # the result should be %d/%m/%Y as the more likely choice. However, at this point,
    # we will allow %m/%d/%Y.
    assert DateInfer.infer(['04/12/2012', '05/12/2012',
                            '06/12/2012', '07/12/2012']) in ['%d/%m/%Y', '%m/%d/%Y']


def test_mode():
    """Test Dateinfer._mode function"""
    assert DateInfer._mode([1, 3, 4, 5, 6, 5, 2, 5, 3]) == 5
    assert DateInfer._mode([1, 2, 2, 3, 3]) == 2  # with ties, pick least value


def test_most_restrictive():
    """Test Dateinfer._most_restrictive function"""
    t = DateInfer._most_restrictive

    assert MonthNum() == t([DayOfMonth(), MonthNum, Year4()])
    assert Year2() == t([Year4(), Year2()])


def test_percent_match():
    """Test Dateinfer._percent_match function"""
    t = DateInfer._percent_match
    patterns = (DayOfMonth, MonthNum, Filler)
    examples = ['1', '2', '24', 'b', 'c']

    percentages = t(patterns, examples)

    assert pytest.approx(percentages[0]) == 0.6  # DayOfMonth 1..31
    assert pytest.approx(percentages[1]) == 0.4  # Month 1..12
    assert pytest.approx(percentages[2]) == 1.0  # Filler any


def test_rule_elements_find():
    """Test find() from rule_elements"""
    elem_list = [Filler(' '), DayOfMonth(), Filler('/'), MonthNum(), Hour24(), Year4()]
    t = ruleproc.Sequence.find

    assert t([Filler(' ')], elem_list) == 0
    assert t([MonthNum], elem_list) == 3
    assert t([Filler('/'), MonthNum()], elem_list) == 2
    assert t([Hour24, Year4()], elem_list) == 4

    elem_list = [
        WeekdayShort, MonthTextShort, Filler(' '), Hour24,
        Filler(':'), Minute, Filler(':'), Second,
        Filler(' '), Timezone, Filler(' '), Year4
    ]

    assert t([Hour24, Filler(':')], elem_list) == 3


def test_rule_elements_match():
    """Test match() from rule_elements"""
    t = ruleproc.Sequence.match

    assert t(Hour12, Hour12)
    assert t(Hour12(), Hour12)
    assert t(Hour12, Hour12())
    assert t(Hour12(), Hour12())
    assert not t(Hour12, Hour24)
    assert not t(Hour12(), Hour24)
    assert not t(Hour12, Hour24())
    assert not t(Hour12(), Hour24())


def test_rule_elements_next():
    """Test next() from rule_elements"""
    elem_list = [
        Filler(' '), DayOfMonth(), Filler('/'),
        MonthNum(), Hour24(), Year4()
    ]

    next1 = ruleproc.Next(DayOfMonth, MonthNum)
    assert next1.is_true(elem_list)

    next2 = ruleproc.Next(MonthNum, Hour24)
    assert next2.is_true(elem_list)

    next3 = ruleproc.Next(Filler, Year4)
    assert not next3.is_true(elem_list)


def test_tag_most_likely():
    """Test DateInfer._tag_most_likely function"""
    examples = ['8/12/2004', '8/14/2004', '8/16/2004', '8/25/2004']
    t = DateInfer._tag_most_likely

    actual = t(examples)
    expected = [MonthNum(), Filler('/'), DayOfMonth(), Filler('/'), Year4()]

    assert actual == expected


def test_tokenize():
    """Test DateInfer._tokenize_by_character_class function"""
    t = DateInfer._tokenize_by_character_class

    assert t('') == []
    assert t('2013-08-14') == ['2013', '-', '08', '-', '14']
    assert t('Sat Jan 11 19:54:52 MST 2014') == [
        'Sat', ' ', 'Jan', ' ', '11', ' ', '19', ':', '54', ':', '52', ' ', 'MST', ' ', '2014']
    assert t('4/30/1998 4:52 am') == ['4', '/', '30', '/', '1998', ' ', '4', ':', '52', ' ', 'am']
