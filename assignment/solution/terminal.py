from colorama import Fore, Style

import db
from option import Option, Query


# The database session object
session = None

# The user currently logged in
current_user = None


def error(text):
    """
    Prints a nicely formatted error message to the screen
    :param text: The error message
    """
    print(f"{Fore.RED}Error{Style.RESET_ALL} {text}\n")


def success(text):
    """
    Prints a nicely formatted success message to the screen
    :param text: The success message
    """
    print(f"{Fore.GREEN}Success{Style.RESET_ALL} {text}\n")


def logout_query():
    """
    Logs out the current user and shows the welcome screen
    """
    print(f"Logout. Goodbye, {current_user.name}.")
    welcome_query()


def login_query():
    """
    Asks for a username and password.
    If the input is valid, shows the main menu; else, goes back to the welcome screen
    """
    global current_user
    print("Login.")

    name = input("Name > ")
    password = input("Password > ")
    password = db.hash_password(password)

    user = db.login(session, name, password)
    if user:
        success(f"Logged in as {name}.")
        current_user = user

        logged_in_query()
    else:
        error("User name or password is wrong. Try again.")
        welcome_query()


def new_user_query():
    """
    Asks for username and password of a new user.
    Aborts and shows the welcome screen as soon as one input is empty.
    Adds a new user to the database and shows the welcome screen
    """
    print("Create a new user.")
    name = input("Name > ")
    password = input("Password > ")

    if name == "":
        error("Name must not be empty.")
        welcome_query()
        return
    if password == "":
        error("Password must not be empty.")
        welcome_query()
        return

    password = db.hash_password(password)

    db.new_user(session, name, password)

    success(f"Created new user '{name}'.")
    welcome_query()


def welcome_query():
    """
    Asks the user to either log in or create a new user
    """
    option_create_login = Option(1, "Log in", login_query)
    option_create_new_user = Option(2, "New user", new_user_query)

    query = Query("Welcome. This is a demo password manager.", [option_create_login, option_create_new_user])
    query.post()


def logged_in_query():
    """
    Shows the main menu
    """
    global current_user

    option_list = Option(1, "View list", list_entries)
    option_show_password = Option(2, "Show entry", show_password)
    option_add_entry = Option(3, "Add entry", add_entry_query)
    option_edit_entry = Option(4, "Edit entry", edit_entry_query)
    option_delete_entry = Option(5, "Delete entry", delete_entry)
    option_logout = Option("l", "Log out", logout_query)

    query = Query(f"What do you want to do, {current_user.name}?",
                  [option_list, option_show_password, option_add_entry,
                   option_edit_entry, option_delete_entry, option_logout])
    query.post()


def list_entries():
    """
    Prints a nicely formatted list of all entries of the current user
    """
    global current_user

    result = db.get_entry_view(current_user)
    print(result)

    logged_in_query()


def show_password():
    """
    Asks for an entry name.
    If it exists, prints the entry information; else, shows the main menu
    """
    global current_user

    print("Show an entry.")
    name = input("Name > ")

    if name == "":
        error("Name must not be empty.")
        logged_in_query()
        return

    entry = db.get_entry(current_user, name)

    if entry:
        print(f"{Fore.CYAN}Name      {Style.RESET_ALL} {entry.name}")
        print(f"{Fore.CYAN}Info      {Style.RESET_ALL} {entry.info}")
        print(f"{Fore.CYAN}Password  {Fore.GREEN} {entry.password}{Style.RESET_ALL}")
        print()
    else:
        error(f"There is no entry named '{name}'. Try again.")

    logged_in_query()


def add_entry_query():
    """
    Asks the user for name, info and password of a new entry.
    Aborts and shows the main menu as soon as one of the inputs is empty.
    Aborts and shows the main menu if there is already an entry with the given name.
    Else, adds a new entry to the database and shows the main menu
    """
    global current_user

    print("Add a new entry.")
    name = input("Name > ")
    if name == "":
        error("Name must not be empty. Try again.")
        logged_in_query()
        return

    info = input("Info > ")
    if info == "":
        error("Info must not be empty. Try again.")
        logged_in_query()
        return

    password = input("Password > ")
    if password == "":
        error("Password must not be empty. Try again.")
        logged_in_query()
        return

    if db.add_entry(session, current_user, name, info, password):
        success(f"Created entry with name '{name}'. View your entries with the list command.")
    else:
        error(f"There is already an entry named '{name}'. Try again.")

    logged_in_query()


def delete_entry():
    """
    Asks the user for an entry name.
    Aborts and shows the main menu if the name is empty.
    Deletes the entry from the database and shows the main menu if the entry exists.
    Else, shows the main menu
    """
    global current_user

    print("Delete an entry.")
    name = input("Name > ")

    if name == "":
        error("Name must not be empty.")
        logged_in_query()
        return

    if db.delete_entry(session, current_user, name):
        success(f"Entry '{name}' deleted.")
    else:
        error(f"There is no entry named '{name}'. Try again.")

    logged_in_query()


def edit_entry_query():
    """
    Asks the user for an entry name.
    Aborts and shows the main menu, if no such entry exists.
    Asks for new name, info and passwords.
    If a field is left blank, the old value remains the same.
    Updates entry in the database and shows the main menu
    :return:
    """
    global current_user

    print("Edit an entry.")
    name = input("Name > ")

    if name == "":
        error("Name must not be empty.")
        logged_in_query()
        return

    entry = db.get_entry(current_user, name)

    if not entry:
        error(f"There is no entry named '{name}'. Try again.")
        logged_in_query()
        return

    print("Leave a field blank if you do not intend to change it")

    new_name = input("New name > ")
    if new_name == "":
        print(f"\033[ANew name > {Fore.GREEN}{entry.name}{Style.RESET_ALL}")
        new_name = entry.name

    new_info = input("New info > ")
    if new_info == "":
        print(f"\033[ANew info > {Fore.GREEN}{entry.info}{Style.RESET_ALL}")
        new_info = entry.info

    new_password = input("New password > ")
    if new_password == "":
        print(f"\033[ANew password > {Fore.GREEN}{entry.password}{Style.RESET_ALL}")
        new_password = entry.password

    db.update_entry(session, entry, new_name, new_info, new_password)

    logged_in_query()