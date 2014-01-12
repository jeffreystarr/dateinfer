import calendar

__author__ = 'jeffrey.starr@ztoztechnologies.com'


class DateElement(object):
    """
    Abstract class for a date element, a portion of a valid date/time string

    Inheriting classes should implement a string 'directive' field that provides the relevant
    directive for the datetime.strftime/strptime method.
    """
    directive = None

    def __eq__(self, other):
        return self.directive == other.directive

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.directive


class DayOfMonth(DateElement):
    """1 .. 31"""

    directive = '%d'

    @staticmethod
    def is_match(token):
        try:
            day = int(token)
            return 1 <= day <= 31
        except ValueError:
            return False


class Filler(DateElement):
    """
    A special date class, filler matches everything. Filler is usually used for matches of whitespace
    and punctuation.
    """
    def __init__(self, filler):
        self.directive = filler.replace('%', '%%')  # escape %

    @staticmethod
    def is_match(token):
        return True


class MonthNum(DateElement):
    """1 .. 12"""

    directive = '%m'

    @staticmethod
    def is_match(token):
        try:
            month = int(token)
            return 1 <= month <= 12
        except ValueError:
            return False


class MonthTextLong(DateElement):
    """January, February, ..., December

    Uses calendar.month_name to provide localization
    """
    directive = '%B'

    @staticmethod
    def is_match(token):
        return token in calendar.month_name


class MonthTextShort(DateElement):
    """Jan, Feb, ... Dec

    Uses calendar.month_abbr to provide localization
    """
    directive = '%b'

    @staticmethod
    def is_match(token):
        return token in calendar.month_abbr


class WeekdayLong(DateElement):
    """Sunday, Monday, ..., Saturday

    Uses calendar.day_name to provide localization
    """
    directive = '%A'

    @staticmethod
    def is_match(token):
        return token in calendar.day_name


class WeekdayShort(DateElement):
    """Sun, Mon, ... Sat

    Uses calendar.day_abbr to provide localization
    """
    directive = '%a'

    @staticmethod
    def is_match(token):
        return token in calendar.day_abbr


class Year2(DateElement):
    """00 .. 99"""

    directive = '%y'

    @staticmethod
    def is_match(token):
        if len(token) != 2:
            return False
        try:
            year = int(token)
            return 0 <= year <= 99
        except:
            return False


class Year4(DateElement):
    """0000 .. 9999"""

    directive = '%Y'

    @staticmethod
    def is_match(token):
        if len(token) != 4:
            return False
        try:
            year = int(token)
            return True
        except:
            return False
