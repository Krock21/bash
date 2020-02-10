import unittest
import bash_builtins
import sys
import tempfile
import os
import bash_tokenize
import interpret
import substitute


class TestBuiltins(unittest.TestCase):
    # private functions, actually
    def setUp(self):
        self.TEST_STRING = "  tes t_co n\nc o\nnt en   t\n \n     \nt es\nt  "
        self.TEST_STRING_WC_INTERACTIVE = "7 11 43"
        self.TEST_STRING_WC = "7 11"  # CONNECTED TO TEST_STRING, first number is lines, second number is words,
        # third number will be added automatically(because of difference in windows and linux)
        self.TEST_ARGUMENTS = ["a rg 1", "arg 2", "arg3_12das", "__dsa"]

    def test_cat(self):
        file = tempfile.NamedTemporaryFile("w", delete=False)
        filename = file.name
        file.write(self.TEST_STRING)
        file.close()
        read_pipe, write_pipe = os.pipe()

        thread = bash_builtins.simple_interpret_single_builtin_command(["cat", file.name],
                                                                       stdin=sys.stdin.fileno(),
                                                                       stdout=write_pipe)
        thread.wait()
        os.remove(filename)
        os.close(write_pipe)
        with open(read_pipe, "r") as fin:
            self.assertEqual(fin.read(), self.TEST_STRING)

    def test_echo(self):
        read_pipe, write_pipe = os.pipe()
        thread = bash_builtins.simple_interpret_single_builtin_command(["echo", *self.TEST_ARGUMENTS],
                                                                       stdin=sys.stdin.fileno(),
                                                                       stdout=write_pipe)
        thread.wait()
        os.close(write_pipe)
        with open(read_pipe, "r") as fin:
            self.assertEqual(fin.read(), ' '.join(self.TEST_ARGUMENTS) + os.linesep)

    def test_wc(self):
        file = tempfile.NamedTemporaryFile("w", delete=False)
        filename = file.name
        file.write(self.TEST_STRING)
        read_pipe, write_pipe = os.pipe()
        file.close()

        thread = bash_builtins.simple_interpret_single_builtin_command(["wc", file.name],
                                                                       stdin=sys.stdin.fileno(),
                                                                       stdout=write_pipe)
        thread.wait()
        os.close(write_pipe)
        with open(read_pipe, "r") as fin:
            file_content = fin.read()
            self.assertEqual(file_content, self.TEST_STRING_WC + " " + str(len(self.TEST_STRING)))
        os.remove(filename)

    def test_interactive_wc(self):
        input_pipe, wcstdin_pipe = os.pipe()
        read_pipe, write_pipe = os.pipe()
        thread = bash_builtins.simple_interpret_single_builtin_command(["wc"],
                                                                       stdin=input_pipe,
                                                                       stdout=write_pipe)
        with open(wcstdin_pipe, "w") as fout:
            fout.write(self.TEST_STRING)
        thread.wait()
        os.close(input_pipe)
        os.close(write_pipe)
        with open(read_pipe, "r") as fin:
            file_content = fin.read()
            self.assertEqual(file_content, self.TEST_STRING_WC_INTERACTIVE)

    def test_pwd(self):
        read_pipe, write_pipe = os.pipe()
        thread = bash_builtins.simple_interpret_single_builtin_command(["pwd"],
                                                                       stdin=sys.stdin.fileno(),
                                                                       stdout=write_pipe)
        thread.wait()
        os.close(write_pipe)
        with open(read_pipe, "r") as fin:
            self.assertEqual(fin.read(), os.getcwd())


class TestTokenize(unittest.TestCase):
    def test_shlex_tokenize(self):
        self.assertEqual("I don't want to test shlex", "I don't want to test shlex")
        self.assertEqual(bash_tokenize.shlex_tokenize("a && b; c && d || e; f >'abc'; (def \"ghi\")"),
                         ['a', '&&', 'b;', 'c', '&&', 'd', '||', 'e;', 'f', '>abc;', '(def', 'ghi)'])


class TestInterpret(unittest.TestCase):
    # private function, actually
    def test_split_by_token(self):
        self.assertEqual(interpret.split_by_token(["a", "b", "|", "|", "c", "|", "d", "|"]),
                         [["a", "b"], [], ["c"], ["d"], []])
        self.assertEqual(interpret.split_by_token(["|", "b", "c", "d", "e", "|", "d", "e"]),
                         [[], ["b", "c", "d", "e"], ["d", "e"]])

    # private function, actually
    def test_simple_interpret_single_command(self):
        waiter = interpret.simple_interpret_single_command([], 0, 1)
        waiter.wait()
        # linux: PermissionError
        # windows: OSError
        with self.assertRaises(OSError):
            waiter = interpret.simple_interpret_single_command([""], 0, 1)
            waiter.wait()
        with self.assertRaises(FileNotFoundError):
            waiter = interpret.simple_interpret_single_command(
                ["random_unrecognized_unused_program_with_unique_name"],
                0, 1)
            waiter.wait()
        read_fd, write_fd = os.pipe()
        waiter = interpret.simple_interpret_single_command(["echo", "hello", "world"], 0, write_fd)
        waiter.wait()
        os.close(write_fd)
        with open(read_fd, "r") as fin:
            self.assertEqual(fin.read(), "hello world" + os.linesep)

        read_fd, write_fd = os.pipe()
        waiter = interpret.simple_interpret_single_command(["git", "version"], 0, write_fd)
        waiter.wait()
        os.close(write_fd)
        os.close(read_fd)

    def test_simple_interpret_commands(self):
        read_fd, write_fd = os.pipe()
        interpret.simple_interpret_commands(["echo", "abc", "def", "ghi", "|", "echo", "qwe", "rty"], stdout=write_fd)
        os.close(write_fd)
        with open(read_fd, "r") as fin:
            self.assertEqual(fin.read(), "qwe rty" + os.linesep)

        read_fd, write_fd = os.pipe()
        # we do not support macos
        interpret.simple_interpret_commands(["echo", "print(str(2 + 3) + \"abc\")\n", "|", "python"],
                                            stdout=write_fd)
        os.close(write_fd)
        with open(read_fd, "r") as fin:
            self.assertEqual(fin.read(), "5abc\n")

        read_fd, write_fd = os.pipe()
        # we do not support macos
        interpret.simple_interpret_commands(["echo", "123", "|", "wc"],
                                            stdout=write_fd)
        os.close(write_fd)
        with open(read_fd, "r") as fin:
            self.assertEqual(fin.read(), "1 1 4")


class TestSubstitute(unittest.TestCase):
    def test_simple_substitute(self):
        os.environ["x"] = "VARIABLE"
        os.environ["var"] = "VARIABLE2"
        self.assertEqual(substitute.simple_substitute("$x '$x $x' \" $x$x $x\""),
                         "VARIABLE '$x $x' \" VARIABLEVARIABLE VARIABLE\"")
        self.assertEqual(substitute.simple_substitute("$x$var '$x $var' \" $var$x $x\""),
                         "VARIABLEVARIABLE2 '$x $var' \" VARIABLE2VARIABLE VARIABLE\"")
        self.assertEqual(substitute.simple_substitute("$y$x$y$var $y'$x $var'$y $y\"$y $var$y$x $y$x$y\"$y"),
                         "VARIABLEVARIABLE2 '$x $var' \" VARIABLE2VARIABLE VARIABLE\"")


if __name__ == '__main__':
    unittest.main()
