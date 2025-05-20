from colorama import Fore, Style


def halt():
    """
    Exits the programme; used by the default quit option
    """
    exit(0)


class Query:
    """
    Capsules a menu screen where the user has to choose between different options
    """
    def __init__(self, text, options):
        """
        :param text: A text describing the menu screen
        :param options: A list of options that are presented to the user.
                        By default, a quit option is added to the list
        """
        self.text = text
        self.quit_option = Option("q", "Quit", halt)
        self.options = options + [self.quit_option]

    def post(self):
        """
        Prints the menu with the given options and asks for an answer.
        If the answer matches an action, the action is performed.
        Else, An error message is shown and the same query is posted again
        """
        print(self.text)
        print(f"Options:")

        for option in self.options:
            option.print_option()

        answer = input("> ")
        print()

        for option in self.options:
            if answer == str(option.n):
                option.action()
                return

        from terminal import error
        error("Not a viable option. Try again.")
        self.post()


class Option:
    def __init__(self, n, text, action):
        """
        :param n: The input that triggers the action
        :param text: A description of the action
        :param action: A function that performs the action
        """
        self.n = n
        self.text = text
        self.action = action

    def print_option(self):
        """
        Prints a line with the trigger input and the option text
        """
        if isinstance(self.n, int):
            print(f"{Fore.CYAN}{self.n:2d}{Style.RESET_ALL} {self.text}")
        else:
            print(f"{Fore.CYAN} {self.n}{Style.RESET_ALL} {self.text}")
