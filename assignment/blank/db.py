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
    


def get_entry(current_user, name):
    """
    Gets an entry from a user by name
    :param current_user: The user that is currently logged in
    :param name: The entry name
    :return: The entry, if it exists; else, None
    """
    # TODO
    


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
    