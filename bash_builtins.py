import re
import os
import argparse
import threading
import signal
import globals


class BuiltinThreadWrapper:
    """
    wraps Thread object. Adds to it wait() method
    """

    def __init__(self, thread_object):
        self.thread = thread_object

    def wait(self):
        self.thread.join()


### BUILTIN_FUNCTIONS

def cat_function(args, stdin, stdout):
    """
    prints 1st argument file
    :param args: arguments
    :param stdin: input file descriptor
    :param stdout: output file descriptor
    :return: nothing
    """
    parser = argparse.ArgumentParser(prog="cat", description='print file content')
    parser.add_argument("FILE", nargs='?', help='path to file')
    parsed_args = vars(parser.parse_args(args))
    fin = None
    if parsed_args.get("FILE"):
        fin = open(parsed_args.get("FILE"), "r")
    else:
        fin = open(stdin, "r", closefd=False)
    with fin, open(stdout, "w", closefd=False) as fout:  # we should not close stdout
        fout.write(fin.read())


def echo_function(args, stdin, stdout):
    """
    prints arguments separated by ' '
    :param args: arguments
    :param stdin: input file descriptor
    :param stdout: output file descriptor
    :return: nothing
    """
    parser = argparse.ArgumentParser(prog="echo", description='print arguments')
    parser.add_argument("argument", nargs='+')
    parsed_args = parser.parse_args(args)
    fout = open(stdout, "w", closefd=False)  # we should not close stdout
    fout.write(' '.join(vars(parsed_args).get("argument")) + os.linesep)


def wc_function(args, stdin, stdout):
    """
    prints count of lines, words and bytes in 1st argument file.
    if file is not specified, prints count of lines, words and bytes in stdin
    :param args: arguments
    :param stdin: input file descriptor
    :param stdout: output file descriptor
    :return: nothing
    """
    parser = argparse.ArgumentParser(prog="wc", description='print number of lines, words and bytes in FILE')
    parser.add_argument("FILE", nargs='?', help='path to file')
    parsed_args = parser.parse_args(args)
    filepath = vars(parsed_args).get("FILE")
    fout = open(stdout, "w", closefd=False)  # we should not close stdout
    fin = None
    if filepath:
        # READ FILEPATH
        fin = open(filepath, "r")
    else:
        # READ STDIN
        fin = open(stdin, "r", closefd=False)

    with fin:
        lines = fin.readlines()
        words_count = sum([len(line.split()) for line in lines])
        file_size = sum([len(line) for line in lines])  # TODO maybe replace with os.path.getsize() for files
        fout.write(str(len(lines)) + " " + str(words_count) + " " + str(file_size))


def pwd_function(args, stdin, stdout):
    """
    prints absolute path to current directory
    :param args: arguments
    :param stdin: input file descriptor
    :param stdout: output file descriptor
    :return: nothing
    """
    parser = argparse.ArgumentParser(prog="pwd", description='print current directory')
    parser.parse_args(args)
    fout = open(stdout, "w", closefd=False)  # we should not close stdout
    fout.write(os.getcwd())


def exit_function(args, stdin, stdout):
    """
    sends SIGTERM to this process.
    :param args: arguments
    :param stdin: input file descriptor
    :param stdout: output file descriptor
    :return: nothing
    """
    globals.set_should_exit(True)


def grep_function(args, stdin, stdout):
    """
    Match lines in FILE or stdin with PATTERN
    :param args: arguments
    :param stdin: input file descriptor
    :param stdout: output file descriptor
    :return: nothing
    """
    parser = argparse.ArgumentParser(prog="grep", description='print lines matching a pattern')
    parser.add_argument("-i", action='store_true',
                        help='Ignore case distinctions, so that characters that differ only in case match each other.')
    parser.add_argument("-w", action='store_true',
                        help='Select  only  those  lines  containing  matches  that form whole words.')
    parser.add_argument("-A", nargs='?', action='store', default=0,
                        help='Print A lines after matched lines')
    parser.add_argument("PATTERN", help='Regular expression to be matched in line')
    parser.add_argument("FILE", nargs='?', help='Path to file to scan for')
    parsed_args = vars(parser.parse_args(args))

    pattern = parsed_args.get("PATTERN")
    if parsed_args.get("w"):
        pattern = r'\b' + pattern + r'\b'
    flags = 0
    if parsed_args.get('i'):
        flags |= re.IGNORECASE

    regexp = re.compile(pattern, flags)

    fin = None
    if parsed_args.get('FILE'):
        fin = open(parsed_args.get('FILE'), 'r', closefd=True)
    else:
        fin = open(stdin, 'r', closefd=False)

    fout = open(stdout, 'w', closefd=False)

    with fin, fout:
        after_parameter = int(parsed_args.get('A'))
        remaining_after = 0
        for line in fin:
            if regexp.search(line):
                remaining_after = after_parameter + 1
            if remaining_after > 0:
                remaining_after -= 1
                fout.write(line)


command_to_function = {
    "cat": cat_function,
    "echo": echo_function,
    "wc": wc_function,
    "pwd": pwd_function,
    "exit": exit_function,
    "grep": grep_function
}


def simple_interpret_single_builtin_command(command, stdin, stdout):
    """
    execute single(without pipes) builtin command with stdin=stdin, stdout=stdout

    :param stdout: output file descriptor
    :param stdin: input file descriptor
    :param command: list of attributes of command
    :return: Object with .wait(), None if command unrecognized
    """
    if len(command) == 0:
        class EmptyCommand:
            def wait(self):
                pass

        return EmptyCommand()

    equality_match = re.match(r"^([\w]+)=(.+)$", command[0])
    if equality_match:
        os.environ[equality_match.group(1)] = equality_match.group(2)

        class Equality:
            def wait(self):
                pass

        return Equality()
    elif command[0] in command_to_function:
        thread = threading.Thread(target=command_to_function.get(command[0]), args=(command[1:], stdin, stdout))
        thread.start()

        return BuiltinThreadWrapper(thread)
    else:
        return None
