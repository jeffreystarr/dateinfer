def infer(examples):
    """
    Returns a datetime.strptime-compliant format string for parsing the *most likely* date format
    used in examples. examples is an iterator containing example date strings.
    """
    return ''


def _infer_with_probabilities(examples):
    """
    Returns a list of 2-tuples: a datetime.strptime-compliant format string and a probability [0-1] for
    the format string to be "correct" given the list of examples date strings.
    """
    return []
