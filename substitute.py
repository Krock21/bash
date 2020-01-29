import os
import re


def replacer(s, new_string, start_index, end_index):
    return s[:start_index] + new_string + s[end_index:]


def get_environment_value(s):
    return os.environ[s] if s in os.environ else ""


def simple_substitute(s):
    matches = re.finditer(r"(\$)(\w+)", s)
    match_positions = []
    for match in matches:
        match_positions.append((match.start(2), match.end(2)))
    match_positions.reverse()
    for (start, end) in match_positions:
        s = replacer(s, get_environment_value(s[start:end]), start - 1, end)  # too slow
    return s
