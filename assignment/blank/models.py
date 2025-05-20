from sqlalchemy import String, Column, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# The object used to collect the metadata of the db tables
Base = declarative_base()


class User(Base):
    """
    Class for a user of the password manager
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    password = Column(String)
    entries = relationship("Entry", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, entries=[{', '.join([str(e) for e in self.entries])}])"


class Entry(Base):
    """
    Class for an entry containing password information
    """
    __tablename__ = "entry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="entries")
    name = Column(String)
    info = Column(String)
    password = Column(String)

    def __repr__(self) -> str:
        return f"Entry(id={self.id!r}, name={self.name!r}), key={self.password!r}"
