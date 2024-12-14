from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///database.db')

Base = declarative_base()

# Define the User database model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True ,nullable=False)
    password = Column(String(100), nullable=False)

    # Relationship with Book and Review table
    book = relationship('Book', back_populates='user', cascade='all, delete-orphan')
    review = relationship('Review', back_populates='userr', cascade='all, delete-orphan')

# Define the Book database model
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationship with User and Review table
    user = relationship('User', back_populates='book')
    reviews = relationship('Review', back_populates='boook', cascade='all, delete-orphan')

# Define the Review database model
class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    content = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)

    # relationship with User and Book table
    userr = relationship('User', back_populates='review',single_parent=True)
    boook = relationship('Book', back_populates='reviews',single_parent=True)

session = sessionmaker(bind=engine)

Session = session()

Base.metadata.create_all(engine)
