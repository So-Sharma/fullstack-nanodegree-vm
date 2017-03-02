from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Item

engine = create_engine('sqlite:///catalog.db')
DBSession = sessionmaker(bind=engine)
session = DBSession()

session.query(Category).delete()
session.query(Item).delete()

session.add_all(
    [
        Category(id=1, name="Fiction"),
        Category(id=2, name="Self-help"),
        Category(id=3, name="Travel"),
        Category(id=4, name="Children's books"),
        Category(id=5, name="Biographies and Memoirs"),
        Category(id=6, name="Computers and Technology")
    ])
session.commit()
