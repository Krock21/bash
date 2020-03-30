# private field of globals.py
__should_exit = False


def get_should_exit():
    return __should_exit


def set_should_exit(value):
    global __should_exit
    __should_exit = value
