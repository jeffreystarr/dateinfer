"""Module with core elements for package"""

import collections
import itertools
import string

from dateinfer.date_elements import DATE_ELEMENTS, Filler
from dateinfer.ruleproc import RULES


class DateInfer:
    """Main class for date infer tasks"""

    @staticmethod
    def infer(examples, alt_rules=None):
        """
        Returns a datetime.strptime-compliant format string for parsing the *most likely*
        date format used in examples. examples is a list containing example date strings.
        """
        date_classes = DateInfer._tag_most_likely(examples)

        if alt_rules:
            date_classes = DateInfer._apply_rewrites(date_classes, alt_rules)
        else:
            date_classes = DateInfer._apply_rewrites(date_classes, RULES)

        date_string = ''
        for date_class in date_classes:
            date_string += date_class.directive

        return date_string

    @staticmethod
    def _apply_rewrites(date_classes, rules):
        """
        Return a list of date elements by applying rewrites to the initial date element list
        """
        for rule in rules:
            date_classes = rule.execute(date_classes)

        return date_classes

    @staticmethod
    def _mode(elems):
        """
        Find the mode (most common element) in list elems. If there are ties,
        this function returns the least value.

        If elems is an empty list, returns None.
        """
        if len(elems) == 0:
            return None

        c = collections.Counter()
        c.update(elems)

        most_common = c.most_common(1)
        most_common.sort()
        return most_common[0][0]  # most_common[0] is a tuple (key, count); no need for the count

    @staticmethod
    def _most_restrictive(date_elems):
        """
        Return the date_elem that has the most restrictive range from date_elems
        """
        most_index = len(DATE_ELEMENTS)
        for date_elem in date_elems:
            if date_elem in DATE_ELEMENTS and DATE_ELEMENTS.index(date_elem) < most_index:
                most_index = DATE_ELEMENTS.index(date_elem)
        if most_index < len(DATE_ELEMENTS):
            return DATE_ELEMENTS[most_index]
        else:
            raise KeyError('No least restrictive date element found')

    @staticmethod
    def _percent_match(date_classes, tokens):
        """
        For each date class, return the percentage of tokens that the class matched
        (floating point [0.0 - 1.0]). The returned value is a tuple of length patterns.
        Tokens should be a list.
        """
        match_count = [0] * len(date_classes)

        for i, date_class in enumerate(date_classes):
            for token in tokens:
                if date_class.is_match(token):
                    match_count[i] += 1

        percentages = tuple([float(m) / len(tokens) for m in match_count])
        return percentages

    @staticmethod
    def _tag_most_likely(examples):
        """
        Return a list of date elements by choosing the most likely element for a token within
        examples (context-free).
        """
        tokenized_examples = [DateInfer._tokenize_by_character_class(example)
                              for example in examples]

        # We currently need the tokenized_examples to all have the same length, so drop instances
        # that have a length that does not equal the mode of lengths within tokenized_examples
        token_lengths = [len(e) for e in tokenized_examples]
        token_lengths_mode = DateInfer._mode(token_lengths)
        tokenized_examples = [example for example in tokenized_examples
                              if len(example) == token_lengths_mode]

        # Now, we iterate through the tokens, assigning date elements based on their likelihood.
        # In cases where the assignments are unlikely for all date elements, assign filler.
        most_likely = []
        for token_index in range(0, token_lengths_mode):
            tokens = [token[token_index] for token in tokenized_examples]
            probabilities = DateInfer._percent_match(DATE_ELEMENTS, tokens)
            max_prob = max(probabilities)
            if max_prob < 0.5:
                most_likely.append(Filler(DateInfer._mode(tokens)))
            else:
                if probabilities.count(max_prob) == 1:
                    most_likely.append(DATE_ELEMENTS[probabilities.index(max_prob)])
                else:
                    choices = []
                    for index, prob in enumerate(probabilities):
                        if prob == max_prob:
                            choices.append(DATE_ELEMENTS[index])
                    most_likely.append(DateInfer._most_restrictive(choices))

        return most_likely

    @staticmethod
    def _tokenize_by_character_class(s):
        """
        Return a list of strings by splitting s (tokenizing) by character class.

        For example:
        _tokenize_by_character_class('Sat Jan 11 19:54:52 MST 2014')
        => ['Sat', ' ', 'Jan', ' ', '11', ' ', '19', ':', '54', ':', '52', ' ', 'MST', ' ', '2014']
        _tokenize_by_character_class('2013-08-14')
        => ['2013', '-', '08', '-', '14']
        """
        character_classes = [
            string.digits, string.ascii_letters,
            string.punctuation, string.whitespace,
        ]

        result = []
        rest = list(s)
        while rest:
            progress = False
            for character_class in character_classes:
                if rest[0] in character_class:
                    progress = True
                    token = ''
                    for take_away in itertools.takewhile(lambda c: c in character_class, rest[:]):
                        token += take_away
                        rest.pop(0)
                    result.append(token)
                    break
            if not progress:  # none of the character classes matched; unprintable character?
                result.append(rest[0])
                rest = rest[1:]

        return result


def infer(examples, alt_rules=None):
    """Returns a datetime.strptime-compliant format string
    for parsing the *most likely* date format used in examples.

    Args:
        examples (list): list containing example date strings.
        alt_rules ([type], optional): [description]. Defaults to None.
    """
    return DateInfer.infer(examples, alt_rules)
