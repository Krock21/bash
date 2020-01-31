import os
import re


def replacer(s, new_string, start_index, end_index):
    """
    replace [start_index, end_index) substring of s by new_string, returns new string

    :param s: initial string
    :param new_string: string to be inserted in [start_index, end_index)
    :param start_index: start index
    :param end_index: end index
    :return: s[:start_index] + new_string + s[end_index:]
    """
    return s[:start_index] + new_string + s[end_index:]


def get_environment_value(s):
    """
    :param s: key
    :return: environment value for "s" key
    """
    return os.environ[s] if s in os.environ else ""


def simple_substitute(s):
    """
    find occurencies of "$variable" and replace them to value of "variable" in the environment for any "variable"
    do not replace "$variable" if it is in single quotes

    :param s: string to process
    :return: new string, where all occurencies of "$variable" replaced to value of "variable" in the environment
    """
    matches = re.finditer(r"(\$)(\w+)", s)
    match_positions = []
    current_index = 0
    is_in_single_quotes = False
    for match in matches:
        start = match.start(2)
        end = match.end(2)
        while current_index < start:
            if s[current_index] == "'":
                is_in_single_quotes = not is_in_single_quotes
            current_index += 1
        if not is_in_single_quotes:
            match_positions.append((start, end))
    match_positions.reverse()
    for (start, end) in match_positions:
        s = replacer(s, get_environment_value(s[start:end]), start - 1, end)  # too slow TODO improve
    return s
