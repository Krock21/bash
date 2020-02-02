import unittest
import bash_builtins
import sys
import tempfile
import os

# command_to_function = {
#     "cat": cat_function,
#     "echo": echo_function,
#     "wc": wc_function,
#     "pwd": pwd_function,
#     "exit": exit_function
# }
import bash_tokenize
import interprete
import substitute


class TestBuiltins(unittest.TestCase):
    # private functions, actually
    def setUp(self):
        self.TEST_STRING = "  tes t_co n\nc o\nnt en   t\n \n     \nt es\nt  "
        self.TEST_STRING_WC = "7 11"  # CONNECTED TO TEST_STRING, first number is lines, second number is words,
        # third number will be added automatically(because of difference in windows and linux)
        self.TEST_ARGUMENTS = ["a rg 1", "arg 2", "arg3_12das", "__dsa"]

    def test_cat(self):
        file = tempfile.NamedTemporaryFile("w", delete=False)
        filename = file.name
        file.write(self.TEST_STRING)
        read_pipe, write_pipe = os.pipe()
        file.close()

        thread = bash_builtins.simple_interprete_single_builtin_command(["cat", file.name],
                                                                        stdin=sys.stdin.fileno(),
                                                                        stdout=write_pipe)
        thread.wait()
        os.remove(filename)
        os.close(write_pipe)
        with open(read_pipe, "r") as fin:
            self.assertEqual(fin.read(), self.TEST_STRING)

    def test_echo(self):
        read_pipe, write_pipe = os.pipe()
        thread = bash_builtins.simple_interprete_single_builtin_command(["echo", *self.TEST_ARGUMENTS],
                                                                        stdin=sys.stdin.fileno(),
                                                                        stdout=write_pipe)
        thread.wait()
        os.close(write_pipe)
        with open(read_pipe, "r") as fin:
            self.assertEqual(fin.read(), ' '.join(self.TEST_ARGUMENTS))

    def test_wc(self):
        file = tempfile.NamedTemporaryFile("w", delete=False)
        filename = file.name
        file.write(self.TEST_STRING)
        read_pipe, write_pipe = os.pipe()
        file.close()

        thread = bash_builtins.simple_interprete_single_builtin_command(["wc", file.name],
                                                                        stdin=sys.stdin.fileno(),
                                                                        stdout=write_pipe)
        thread.wait()
        os.close(write_pipe)
        with open(read_pipe, "r") as fin:
            file_content = fin.read()
            self.assertEqual(file_content, self.TEST_STRING_WC + " " + str(os.path.getsize(filename)))
        os.remove(filename)

    def test_pwd(self):
        read_pipe, write_pipe = os.pipe()
        thread = bash_builtins.simple_interprete_single_builtin_command(["pwd"],
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


class TestInterprete(unittest.TestCase):
    # private function, actually
    def test_split_by_token(self):
        self.assertEqual(interprete.split_by_token(["a", "b", "|", "|", "c", "|", "d", "|"]),
                         [["a", "b"], [], ["c"], ["d"], []])
        self.assertEqual(interprete.split_by_token(["|", "b", "c", "d", "e", "|", "d", "e"]),
                         [[], ["b", "c", "d", "e"], ["d", "e"]])

    # private function, actually
    def test_simple_interprete_single_command(self):
        waiter = interprete.simple_interprete_single_command([], 0, 1)
        waiter.wait()
        # linux: PermissionError
        # windows: OSError
        with self.assertRaises(OSError):
            waiter = interprete.simple_interprete_single_command([""], 0, 1)
            waiter.wait()
        with self.assertRaises(FileNotFoundError):
            waiter = interprete.simple_interprete_single_command(
                ["random_unrecognized_unused_program_with_unique_name"],
                0, 1)
            waiter.wait()
        read_fd, write_fd = os.pipe()
        waiter = interprete.simple_interprete_single_command(["echo", "hello", "world"], 0, write_fd)
        waiter.wait()
        os.close(write_fd)
        with open(read_fd, "r") as fin:
            self.assertEqual(fin.read(), "hello world")

        waiter = interprete.simple_interprete_single_command(["git", "version"], 0, write_fd)
        waiter.wait()

    def test_simple_interprete_commands(self):
        read_fd, write_fd = os.pipe()
        interprete.simple_interprete_commands(["echo", "abc", "def", "ghi", "|", "echo", "qwe", "rty"], stdout=write_fd)
        os.close(write_fd)
        with open(read_fd, "r") as fin:
            self.assertEqual(fin.read(), "qwe rty")
        read_fd, write_fd = os.pipe()
        # we do not support macos
        interprete.simple_interprete_commands(["echo", "print(str(2 + 3) + \"abc\")\n", "|", "python"],
                                              stdout=write_fd)
        os.close(write_fd)
        with open(read_fd, "r") as fin:
            self.assertEqual(fin.read(), "5abc\n")


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
