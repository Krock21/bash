import sys
import re
import os
import subprocess
from typing import List


def replacer(s, newstring, startIndex, endIndex):
    return s[:startIndex] + newstring + s[endIndex:]


def environmentValue(s):
    return os.environ[s] if s in os.environ else ""


def simpleTokenize(s):
    # token = '|' OR "(\W)+"
    tokens = re.findall(r"[^\s\|\"\']+|\||\"[^\"]*\"|\'[^\']*\'", s)  # word | (| symbol) | "smth" | 'smth'
    return tokens


def simpleSubstitute(s: str):
    matches = re.finditer(r"(\$)(\w+)", s)
    matchPositions = []
    for match in matches:
        matchPositions.append((match.start(2), match.end(2)))
    matchPositions.reverse()
    for (start, end) in matchPositions:
        s = replacer(s, environmentValue(s[start:end]), start - 1, end)  # too slow
    return s


def splitByToken(tokens, token="|") -> List[List[str]]:
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


def simpleInterpreteSingleCommand(command, stdin, stdout):
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


def simpleInterpreteCommands(tokens):
    commands = splitByToken(tokens)

    # we should not read from sys.stdin until first process has executed
    previousStdin = sys.stdin.fileno()
    if len(commands) == 0:
        return

    processes = []
    for i in range(len(commands) - 1):
        stdinPipe, stdoutPipe = os.pipe()
        processes.append(
            (
                simpleInterpreteSingleCommand(commands[i], stdin=previousStdin, stdout=stdoutPipe),
                (previousStdin, stdoutPipe)
            )
        )
        previousStdin = stdinPipe
    processes.append(
        (
            simpleInterpreteSingleCommand(commands[-1], stdin=previousStdin, stdout=sys.stdout.fileno()),
            (previousStdin, sys.stdout.fileno())
        )
    )

    for (process, (stdinPipe, stdoutPipe)) in processes:
        process.wait()
        if stdinPipe != sys.stdin.fileno():
            os.close(stdinPipe)
        if stdoutPipe != sys.stdout.fileno():
            os.close(stdoutPipe)


def main():
    readCommand = input
    tokenize = simpleTokenize
    substitute = simpleSubstitute
    while True:
        command = readCommand()
        tokens = tokenize(command)
        substitutedCommand = " ".join(
            [substitute(token) if len(token) > 0 and token[0] != "'" else token for token in tokens])
        substitutedTokens = tokenize(substitutedCommand)
        simpleInterpreteCommands(substitutedTokens)


if __name__ == "__main__":
    main()
