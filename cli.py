from bash_tokenize import shlex_tokenize
from substitute import simple_substitute
from interprete import simple_interprete_commands
import sys
import signal


def run_cli():
    """
    runs CommandLine bash-like interface
    :return: nothing
    """
    # calls when process has terminated, usually by exit command
    def sigterm_handler(signalnum, current_stack_frame):
        print("EXITING...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, sigterm_handler)
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
        except ValueError as value_error:
            print(str(value_error))
        except PermissionError as permission_error:
            print(permission_error.strerror)
        except FileNotFoundError as file_not_found_error:
            print(file_not_found_error.strerror)


if __name__ == "__main__":
    run_cli()
