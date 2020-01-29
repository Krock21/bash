import re


def simple_tokenize(s):
    tokens = re.findall(r"[^\s|\"\']+|\||\"[^\"]*\"|\'[^\']*\'", s)  # word | (| symbol) | "smth" | 'smth'
    return tokens
