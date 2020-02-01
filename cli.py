import sys

from bash_tokenize import shlex_tokenize
from substitute import simple_substitute
from interprete import simple_interprete_commands


def run_cli():
    read_command = input
    tokenize = shlex_tokenize
    substitute = simple_substitute
    interprete = simple_interprete_commands
    while True:
        try:
            command = read_command()
            substituted_command = substitute(command)
            substituted_tokens = tokenize(substituted_command)
            interprete(substituted_tokens)
        except KeyboardInterrupt:
            raise
        except FileNotFoundError as file_not_found_error:
            print("Command not found: " + file_not_found_error.filename)


if __name__ == "__main__":
    run_cli()
