import shlex


def shlex_tokenize(s):
    """
    tokenize using shlex.split()
    :param s: string to be tokenized
    :return: list of strings-tokens
    """
    return shlex.split(s)
