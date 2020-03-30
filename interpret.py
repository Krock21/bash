import sys
import subprocess
import os
import bash_builtins
from typing import List


def split_by_token(tokens, token="|") -> List[List[str]]:
    """
    split list of tokens into list of lists of tokens, by token delimeter

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


def simple_interpret_single_command(command, stdin, stdout):
    """
    execute single(without pipes) command with stdin=stdin, stdout=stdout

    :param stdout: output file descriptor
    :param stdin: input file descriptor
    :param command: list of attributes of command
    :return: Popen object for unrecognized, object with .wait() for builtin command
    """
    answer = bash_builtins.simple_interpret_single_builtin_command(command, stdin, stdout)
    if answer:
        return answer
    else:
        return subprocess.Popen(command, bufsize=0, stdin=stdin, stdout=stdout, env=os.environ)


def simple_interpret_commands(tokens, stdin=sys.stdin.fileno(), stdout=sys.stdout.fileno()):
    """
    interpret tokens as bash command(maybe with pipes).

    :param stdout: stdout file descriptor for command
    :param stdin: stdin file descriptor for command
    :param tokens: list of strings
    :return: nothing
    """
    commands = split_by_token(tokens, "|")
    if len(commands) > 1 and any(element == [] for element in commands):
        raise SyntaxError("Empty command with pipes is restricted")

    # we should not read from sys.stdin until first process has executed
    # TODO improve
    # processes should not close file descriptors
    previous_stdin = stdin
    last_stdout = stdout

    processes = []
    for i in range(len(commands) - 1):
        stdin_pipe, stdout_pipe = os.pipe()
        processes.append(
            (
                simple_interpret_single_command(commands[i], stdin=previous_stdin, stdout=stdout_pipe),
                (previous_stdin, stdout_pipe)
            )
        )
        previous_stdin = stdin_pipe
    processes.append(
        (
            simple_interpret_single_command(commands[-1], stdin=previous_stdin, stdout=last_stdout),
            (previous_stdin, last_stdout)
        )
    )

    for (process, (stdin_pipe, stdout_pipe)) in processes:
        process.wait()
        if stdin_pipe != stdin:
            os.close(stdin_pipe)
        if stdout_pipe != stdout:
            os.close(stdout_pipe)
