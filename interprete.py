import sys
import subprocess
import os
from typing import List


def split_by_token(tokens, token="|") -> List[List[str]]:
    """
    :param tokens: list of strings with tokens
    :param token: token-splitter
    :return: list of lists, where particular list consists of command from token to token, not inclusive
    """
    # using list comprehension + zip() + slicing + enumerate()
    # Split list into lists by particular value
    size = len(tokens)
    idx_list = [idx for idx, val in enumerate(tokens) if val == token]  # indicies of token

    res = [tokens[i + 1: j] for i, j in
           zip([-1] + idx_list, idx_list + [size])]

    return res


def simple_interprete_single_command(command, stdin, stdout):
    """
    execute command with stdin=stdin, stdout=stdout

    :param stdout: output file descriptor
    :param stdin: input file descriptor
    :param command: list of attributes of command
    :return: Popen object for unrecognized, object with .wait() for builtin command
    """
    if len(command) > 0 and command[0] == "exit":
        sys.exit(0)
    return subprocess.Popen(command, bufsize=0, stdin=stdin, stdout=stdout, env=os.environ)


def simple_interprete_commands(tokens):
    commands = split_by_token(tokens)

    # we should not read from sys.stdin until first process has executed
    # TODO improve
    previous_stdin = sys.stdin.fileno()
    if len(commands) == 0:
        return

    processes = []
    for i in range(len(commands) - 1):
        stdin_pipe, stdout_pipe = os.pipe()
        processes.append(
            (
                simple_interprete_single_command(commands[i], stdin=previous_stdin, stdout=stdout_pipe),
                (previous_stdin, stdout_pipe)
            )
        )
        previous_stdin = stdin_pipe
    processes.append(
        (
            simple_interprete_single_command(commands[-1], stdin=previous_stdin, stdout=sys.stdout.fileno()),
            (previous_stdin, sys.stdout.fileno())
        )
    )

    for (process, (stdin_pipe, stdout_pipe)) in processes:
        process.wait()
        if stdin_pipe != sys.stdin.fileno():
            os.close(stdin_pipe)
        if stdout_pipe != sys.stdout.fileno():
            os.close(stdout_pipe)
