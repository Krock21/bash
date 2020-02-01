import sys
import re
import os
import argparse
import threading

class BuiltinThreadWrapper:
    def __init__(self, thread_object):
        self.thread = thread_object

    def wait(self):
        self.thread.join()

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

    # TODO maybe create better solution
    if command[0] == "exit":
        sys.exit(0)

    equality_match = re.match(r"^([\w]+)=(.+)$", command[0])
    if equality_match:
        os.environ[equality_match.group(1)] = equality_match.group(2)

        class Equality:
            def wait(self):
                pass

        return Equality()
    elif command[0] == "cat":
        def cat_function():
            parser = argparse.ArgumentParser(prog="cat", description='print file content')
            parser.add_argument("FILE", help='path to file')
            args = parser.parse_args(command[1:])
            fin = open(vars(args).get("FILE"))
            fout = open(stdout, "w", closefd=False)  # we should not close stdout
            fout.write(fin.read() + "\n")

        thread = threading.Thread(target=cat_function)
        thread.start()

        return BuiltinThreadWrapper(thread)
    elif command[0] == "echo":
        def echo_function():
            parser = argparse.ArgumentParser(prog="echo", description='print arguments')
            parser.add_argument("argument", nargs='+')
            args = parser.parse_args(command[1:])
            fout = open(stdout, "w", closefd=False)  # we should not close stdout
            fout.write(' '.join(vars(args).get("argument")) + "\n")

        thread = threading.Thread(target=echo_function)
        thread.start()

        return BuiltinThreadWrapper(thread)
    elif command[0] == "wc":
        def wc_function():
            parser = argparse.ArgumentParser(prog="wc", description='print number of lines, words and bytes in FILE')
            parser.add_argument("FILE", help='path to file')
            args = parser.parse_args(command[1:])
            filepath = vars(args).get("FILE")
            fin = open(filepath)
            fout = open(stdout, "w", closefd=False)  # we should not close stdout
            lines = fin.readlines()
            words_count = sum([len(line.split()) for line in lines])
            file_size = os.path.getsize(filepath)
            fout.write(str(len(lines)) + " " + str(words_count) + " " + str(file_size) + "\n")

        thread = threading.Thread(target=wc_function)
        thread.start()

        return BuiltinThreadWrapper(thread)
    elif command[0] == "pwd":
        def pwd_function():
            parser = argparse.ArgumentParser(prog="pwd", description='print current directory')
            parser.parse_args(command[1:])
            fout = open(stdout, "w", closefd=False)  # we should not close stdout
            fout.write(os.getcwd() + "\n")

        thread = threading.Thread(target=pwd_function)
        thread.start()

        return BuiltinThreadWrapper(thread)
    else:
        return None
