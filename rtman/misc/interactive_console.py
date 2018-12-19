import readline
import code
import rlcompleter


def get_console(variables, greeting="Entering interactive mode. Press ^D to exit."):
    """
    Enter an interactive console.

    variables: dict containing variables that are available directly in the console.

    supports a help function that displays the documentation of objects and functions

    supports tab completion
    """
    readline.parse_and_bind("tab: complete")
    readline.set_completer(rlcompleter.Completer(variables).complete)
    console = code.InteractiveConsole(variables)
    console.interact(greeting)
