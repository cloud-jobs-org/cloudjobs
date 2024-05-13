from datetime import datetime

from sqlalchemy.orm import relationship

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine
from sqlalchemy import Column, Integer, String, DateTime, inspect, ForeignKey, Text


class InventoryEntriesORM(Base):
    __tablename__ = "inventory_entries"
    entry_id = Column(String(ID_LEN), primary_key=True)
    product_id = Column(String(ID_LEN), ForeignKey('products.product_id'))  # ForeignKey to ProductsORM
    amount = Column(Integer)
    entry_datetime = Column(String(32))
    reason = Column(String(32))
    price = Column(Integer)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        return {
            'entry_id': self.entry_id,
            'product_id': self.product_id,
            'amount': self.amount,
            'entry_datetime': self.entry_datetime,
            'reason': self.reason,
            'price': self.price
        }


class ProductsORM(Base):
    __tablename__ = "products"

    category_id = Column(String(ID_LEN), ForeignKey('categories.category_id'))  # ForeignKey to CategoriesORM
    product_id = Column(String(ID_LEN), primary_key=True)
    name = Column(String(255))
    description = Column(Text)
    img_link = Column(String(255))
    cost_price = Column(Integer)
    sale_price = Column(Integer)
    inventory_entries = relationship('InventoryEntriesORM', backref='product')  # Relationship with InventoryEntriesORM

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'img_link': self.img_link,
            'cost_price': self.cost_price,
            'sale_price': self.sale_price,
            'inventory_entries': [entry.to_dict() for entry in self.inventory_entries]  # Include inventory_entries
        }


class CategoryORM(Base):
    __tablename__ = 'categories'
    category_id = Column(String(ID_LEN), primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    img_link = Column(String(255))
    products_list = relationship('ProductsORM', backref='category')

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    @classmethod
    def delete_table(cls):
        if inspect(engine).has_table(cls.__tablename__):
            cls.__table__.drop(bind=engine)

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'img_link': self.img_link,
            'products_list': [product.to_dict() for product in self.products_list]  # Include products_list
        }
