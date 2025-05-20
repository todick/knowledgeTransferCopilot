import click
import sqlalchemy as db
from sqlalchemy.orm import Session

import terminal
from models import Base


def create_session(path):
    """
    Creates a database connection to a SQLite database.
    If the db file is not present, create a new one.
    :path: The path to the db file.
    :return: The connection to the database if succeeded, else None.
    """
    try:
        engine = db.create_engine(f"sqlite:///{path}")

        # Create tables
        Base.metadata.create_all(engine)

        return Session(engine)
    except:
        return None


@click.command()
@click.argument("path")
def start(path):
    """
    Called upon starting the programme.
    :param path: The argument the user passes via the command line which represents the path to the database file.
    """
    # Get session to the db
    session = create_session(path)
    if not session:
        print(f"Error while connecting to db at {path}")
        print("Exiting")
        exit(1)

    # Start the main loop
    terminal.session = session
    terminal.welcome_query()

    # Close the db session if the programme is finished
    session.close()


if __name__ == '__main__':
    # enables ANSI support on the console
    from colorama import init, deinit
    init()

    start()

    # disables the colorama package
    deinit()
