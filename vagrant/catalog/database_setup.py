from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    items = relationship("Item", back_populates="category")

    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'items': self.serialize_items
        }

    @property
    def serialize_items(self):

        return [i.serialize for i in self.items]


class Item(Base):
    __tablename__ = 'item'

    item_id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    created_on = Column(DateTime(timezone=True), default=func.now())
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="items")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")

    # This function is used to enable sending JSON objects in a
    # serializable format
    @property
    def serialize(self):

        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'created_on': self.created_on,
            'category_id': self.category_id,
            'user_id': self.user_id
        }

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
