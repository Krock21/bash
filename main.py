from bash_tokenize import shlex_tokenize
from substitute import simple_substitute
from interprete import simple_interprete_commands


def main():
    read_command = input
    tokenize = shlex_tokenize
    substitute = simple_substitute
    interprete = simple_interprete_commands
    while True:
        command = read_command()
        substituted_command = substitute(command)
        substituted_tokens = tokenize(substituted_command)
        interprete(substituted_tokens)


if __name__ == "__main__":
    main()
