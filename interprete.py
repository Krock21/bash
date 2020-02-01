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


def simple_interprete_single_command(command, stdin, stdout):
    """
    execute single(without pipes) command with stdin=stdin, stdout=stdout

    :param stdout: output file descriptor
    :param stdin: input file descriptor
    :param command: list of attributes of command
    :return: Popen object for unrecognized, object with .wait() for builtin command
    """
    answer = bash_builtins.simple_interprete_single_builtin_command(command, stdin, stdout)
    if answer:
        return answer
    else:
        return subprocess.Popen(command, bufsize=0, stdin=stdin, stdout=stdout, env=os.environ)


def simple_interprete_commands(tokens, stdin=sys.stdin.fileno(), stdout=sys.stdout.fileno()):
    """
    interprete tokens as bash command(maybe with pipes).

    :param stdout: stdout file descriptor for command
    :param stdin: stdin file descriptor for command
    :param tokens: list of strings
    :return: nothing
    """
    commands = split_by_token(tokens, "|")

    # we should not read from sys.stdin until first process has executed
    # TODO improve
    previous_stdin, program_stdout = os.pipe()
    result_stdin, last_stdout = os.pipe()

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
            simple_interprete_single_command(commands[-1], stdin=previous_stdin, stdout=last_stdout),
            (previous_stdin, last_stdout)
        )
    )

    # TODO we could redirect our stdin to first program_stdout
    os.close(program_stdout)

    for (process, (stdin_pipe, stdout_pipe)) in processes:
        process.wait()
        os.close(stdin_pipe)
        os.close(stdout_pipe)

    while True:
        obj = os.read(result_stdin, 1)
        if obj:
            os.write(stdout, obj)
        else:
            break

    os.close(result_stdin)
