import collections
import re
import string
from date_elements import DayOfMonth, MonthNum, MonthTextLong, MonthTextShort, WeekdayLong, WeekdayShort, Year2, Year4, Filler
from ruleproc import *

DATE_ELEMENTS = (DayOfMonth, MonthNum, MonthTextLong, MonthTextShort, WeekdayLong, WeekdayShort, Year2, Year4)

RULES = [
    If(Contains(MonthNum, MonthTextLong), Swap(MonthNum, DayOfMonth)),
    If(Contains(MonthNum, MonthTextShort), Swap(MonthNum, DayOfMonth))
]

def infer(examples, alt_rules=None):
    """
    Returns a datetime.strptime-compliant format string for parsing the *most likely* date format
    used in examples. examples is a list containing example date strings.
    """
    date_classes = _tag_most_likely(examples)

    if alt_rules:
        date_classes = _apply_rewrites(date_classes, alt_rules)
    else:
        date_classes = _apply_rewrites(date_classes, RULES)

    date_string = ''
    for date_class in date_classes:
        date_string += date_class.directive

    return date_string


def _apply_rewrites(date_classes, rules):
    """
    Return a list of date elements by applying rewrites to the initial date element list
    """
    for rule in rules:
        date_classes = rule.execute(date_classes)

    return date_classes


def _mode(elems):
    """
    Find the mode (most common element) in list elems. If there are ties, this function returns the least value.

    If elems is an empty list, returns None.
    """
    if len(elems) == 0:
        return None

    c = collections.Counter()
    c.update(elems)

    most_common = c.most_common(1)
    most_common.sort()
    return most_common[0][0]  # most_common[0] is a tuple of key and count; no need for the count


def _most_restrictive(date_elems):
    """
    Return the date_elem that has the most restrictive range from date_elems
    """
    restrictivity = [MonthNum(), DayOfMonth(), Year2(), Year4(),
                     MonthTextShort(), MonthTextLong(),
                     WeekdayShort(), WeekdayLong()]
    most_index = len(restrictivity)
    for date_elem in date_elems:
        if date_elem in restrictivity and restrictivity.index(date_elem) < most_index:
            most_index = restrictivity.index(date_elem)
    if most_index < len(restrictivity):
        return restrictivity[most_index]
    else:
        raise KeyError('No least restrictive date element found')


def _percent_match(date_classes, tokens):
    """
    For each date class, return the percentage of tokens that the class matched (floating point [0.0 - 1.0]). The
    returned value is a tuple of length patterns. Tokens should be a list.
    """
    match_count = [0] * len(date_classes)

    for i, date_class in enumerate(date_classes):
        for token in tokens:
            if date_class.is_match(token):
                match_count[i] += 1

    percentages = tuple([float(m) / len(tokens) for m in match_count])
    return percentages


def _tag_most_likely(examples):
    """
    Return a list of date elements by choosing the most likely element for a token within examples (context-free).
    """
    tokenized_examples = [_tokenize_by_character_class(example) for example in examples]

    # We currently need the tokenized_examples to all have the same length, so drop instances that have a length
    # that does not equal the mode of lengths within tokenized_examples
    token_lengths = [len(e) for e in tokenized_examples]
    token_lengths_mode = _mode(token_lengths)
    tokenized_examples = [example for example in tokenized_examples if len(example) == token_lengths_mode]

    # Now, we iterate through the tokens, assigning date elements based on their likelihood. In cases where
    # the assignments are unlikely for all date elements, assign filler.
    most_likely = []
    for token_index in range(0, token_lengths_mode):
        tokens = [token[token_index] for token in tokenized_examples]
        probabilities = _percent_match(DATE_ELEMENTS, tokens)
        max_prob = max(probabilities)
        if max_prob < 0.5:
            most_likely.append(Filler(_mode(tokens)))
        else:
            if probabilities.count(max_prob) == 1:
                most_likely.append(DATE_ELEMENTS[probabilities.index(max_prob)]())
            else:
                choices = []
                for index, prob in enumerate(probabilities):
                    if prob == max_prob:
                        choices.append(DATE_ELEMENTS[index]())
                most_likely.append(_most_restrictive(choices))

    return most_likely

def _tokenize_by_character_class(s):
    """
    Return a list of strings by splitting s (tokenizing) by character class.

    For example:
    _tokenize_by_character_class('Sat Jan 11 19:54:52 MST 2014') => ['Sat', ' ', 'Jan', ' ', '11', ' ', '19', ':',
        '54', ':', '52', ' ', 'MST', ' ', '2014']
    _tokenize_by_character_class('2013-08-14') => ['2013', '-', '08', '-', '14']
    """
    character_classes = map(lambda chars: r"^[{0}]+".format(chars),
                            [string.digits, string.letters, string.punctuation, string.whitespace])

    result = []
    rest = s
    while rest:
        progress = False
        for character_class in character_classes:
            match = re.match(character_class, rest)
            if match:
                progress = True
                take_away = match.group(0)
                rest = rest[len(take_away):]
                result.append(take_away)
                break
        if not progress:  # none of the character classes matched; unprintable character?
            result.append(rest[0])
            rest = rest[1:]

    return result
