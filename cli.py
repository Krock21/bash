from bash_tokenize import shlex_tokenize
from substitute import simple_substitute
from interpret import simple_interpret_commands
import sys
import signal
import globals


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
    interpret = simple_interpret_commands
    while not globals.get_should_exit():
        try:
            command = read_command()
            substituted_command = substitute(command)
            substituted_tokens = tokenize(substituted_command)
            interpret(substituted_tokens)
        except KeyboardInterrupt:
            raise
        except SyntaxError as syntax_error:
            print(str(syntax_error))
        except ValueError as value_error:
            print(str(value_error))
        except PermissionError as permission_error:
            print(permission_error.strerror)
        except FileNotFoundError as file_not_found_error:
            print(file_not_found_error.strerror)


if __name__ == "__main__":
    run_cli()
