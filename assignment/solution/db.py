import hashlib
from functools import reduce
from models import User, Entry


def pad_str(text, total_length, front=True):
    """
    Extends a given string with spaces
    :param text: The text to extend
    :param total_length: How long the final string should be
    :param front: True, if spaces are added at the frond; False if spaces are added at the back
    :return: The padded text
    """
    # TODO
    padding = " " * (total_length - len(text))

    if front:
        return f"{padding}{text}"
    else:
        return f"{text}{padding}"


def hash_password(password):
    """
    Computes the MD5 hash of a given string
    :param password: The password to hash
    :return: The has as a string
    """
    return str(hashlib.md5(password.encode()).hexdigest())


def new_user(session, name, password):
    """
    Adds a new user to the database
    :param session: The db session object
    :param name: The user's name
    :param password: The user's password as a hash
    """
    # TODO
    user = User()
    user.name = name
    user.password = password
    user.entries = []
    session.add(user)
    session.commit()


def login(session, name, password):
    """
    Checks whether a user with a given name and password exists
    :param session: The db session object
    :param name: The user's name
    :param password: The user's password as a hash
    :return: The user object, if the user exists and, thus, can
             be logged in; else None
    """
    # TODO
    users = session.query(User)

    for user in users:
        if name == user.name and password == user.password:
            return user
    return None


def add_entry(session, user, name, info, password):
    """
    Adds an entry to the database
    :param session: The db session object
    :param user: The user who is currently logged in
    :param name: The entry name
    :param info: The entry info
    :param password: The entry password
    :return: False, if there is already an entry with that name; in this case nothing is added.
             True, if there is no other entry with the given name; then, it is added to the database
    """
    # TODO
    entries = user.entries
    for entry in entries:
        if entry.name == name:
            return False

    entry = Entry()
    entry.name = name
    entry.info = info
    entry.password = password
    entry.user = user
    session.add(entry)
    session.commit()
    return True


def delete_entry(session, user, name):
    """
    Deletes an entry from the database
    :param session: The db session object
    :param user: The user the entry belongs to
    :param name: The entry name
    :return: True, if the entry exists; in this case, it is deleted.
             False, if not; in this case, nothing happens
    """
    # TODO
    entries = user.entries
    for entry in entries:
        if entry.name == name:
            session.delete(entry)
            session.commit()
            return True
    return False


def get_entry_view(current_user):
    """
    Composes a string of all entries as a padded table
    :param current_user: The user that is currently logged in
    :return: A nicely formatted string of all entries of that user in the following format:
             Let n_name be the length of the longest value in the name column (including the caption "Name")
             Let n_info be the length of the longest value in the name column (including the caption "Info")
             Let s be two spaces "  "
             Let e_i be the entries from i = 1 .. n
             Then print the following table:
             [s]["Name" padded with spaces to n_name at the back][s]["Info" padded with spaces to n_info at the back][s]Password
             [s][e_i.name padded with spaces to n_name at the front][s][e_i.info padded with spaces to n_info at the front][s]["*****" padded with spaces to 8 at the front]
             The last character is supposes to be "\n"
             
             Example:
               Name    Info      Password
                 Mail  cd@ef.de     *****
               Paypal   a@b.com     *****

    """
    # TODO
    result = ""
    entries = current_user.entries

    caption_name = "Name"
    caption_info = "Info"
    caption_password = "Password"
    space = "  "

    max_len_name = reduce(max, list(map(lambda e: len(e.name), entries)) + [len(caption_name)])
    max_len_info = reduce(max, list(map(lambda e: len(e.info), entries)) + [len(caption_info)])

    result += f"{space}{pad_str(caption_name, max_len_name, False)}{space}" \
              f"{pad_str(caption_info, max_len_info, False)}" \
              f"{space}{caption_password}\n"

    for entry in entries:
        result += f"{space}{pad_str(entry.name, max_len_name)}{space}" \
                  f"{pad_str(entry.info, max_len_info)}{space}" \
                  f"{pad_str('*****', 8)}\n"

    return result


def get_entry(current_user, name):
    """
    Gets an entry from a user by name
    :param current_user: The user that is currently logged in
    :param name: The entry name
    :return: The entry, if it exists; else, None
    """
    # TODO
    entries = current_user.entries

    for entry in entries:
        if entry.name == name:
            return entry

    return None


def update_entry(session, entry, name, info, password):
    """
    Updates an entry in the database
    :param session: The db session object
    :param entry: The entry object to update
    :param name: The new entry name
    :param info: The new entry info
    :param password: The new entry password
    """
    # TODO
    entry.name = name
    entry.info = info
    entry.password = password
    session.commit()
