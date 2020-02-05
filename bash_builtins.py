import re
import os
import argparse
import threading
import signal


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
    parser.add_argument("FILE", help='path to file')
    parsed_args = parser.parse_args(args)
    fin = open(vars(parsed_args).get("FILE"), "r")
    fout = open(stdout, "w", closefd=False)  # we should not close stdout
    fout.write(fin.read())
    fin.close()


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
    fout.write(' '.join(vars(parsed_args).get("argument")))


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
    if filepath:
        # READ FILEPATH
        fin = open(filepath, "r")
        lines = fin.readlines()
        words_count = sum([len(line.split()) for line in lines])
        file_size = os.path.getsize(filepath)
        fout.write(str(len(lines)) + " " + str(words_count) + " " + str(file_size))
        fin.close()
    else:
        # READ STDIN
        fin = open(stdin, "r", closefd=False)
        lines = fin.readlines()
        words_count = sum([len(line.split()) for line in lines])
        file_size = sum([len(line) for line in lines])
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
    os.kill(os.getpid(), signal.SIGTERM)


command_to_function = {
    "cat": cat_function,
    "echo": echo_function,
    "wc": wc_function,
    "pwd": pwd_function,
    "exit": exit_function
}


def simple_interprete_single_builtin_command(command, stdin, stdout):
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
