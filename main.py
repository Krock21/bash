from tokenize import simple_tokenize
from substitute import simple_substitute
from interprete import simple_interprete_commands


def main():
    read_command = input
    tokenize = simple_tokenize
    substitute = simple_substitute
    interprete = simple_interprete_commands
    while True:
        command = read_command()
        tokens = tokenize(command)
        substituted_command = " ".join(
            [substitute(token) if len(token) > 0 and token[0] != "'" else token for token in tokens])
        substituted_tokens = tokenize(substituted_command)
        interprete(substituted_tokens)


if __name__ == "__main__":
    main()
