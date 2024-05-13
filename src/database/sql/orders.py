from datetime import datetime

from sqlalchemy.orm import relationship

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine
from sqlalchemy import Column, Integer, String, DateTime, inspect, ForeignKey


class OrderItemORM(Base):
    __tablename__ = "order_item"
    item_id: str = Column(String(ID_LEN), primary_key=True)
    order_id = Column(String(ID_LEN), ForeignKey('orders.order_id'))
    product_id: str = Column(String(ID_LEN))
    product_name: str = Column(String(NAME_LEN))
    price: int = Column(Integer)
    quantity: int = Column(Integer)
    discount_percent: int = Column(Integer)
    # Define relationship
    order = relationship("OrderORM", back_populates="items_ordered")

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
            'item_id': self.item_id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'price': self.price,
            'quantity': self.quantity,
            'discount_percent': self.discount_percent
        }


class OrderORM(Base):
    __tablename__ = 'orders'

    order_id = Column(String(ID_LEN), primary_key=True)
    customer_id = Column(String(ID_LEN))
    customer_name = Column(String(NAME_LEN))
    email = Column(String(255))
    phone = Column(String(18))
    address_id = Column(String(ID_LEN))

    order_datetime = Column(String(32))
    status = Column(String(32))
    # Define relationship
    items_ordered = relationship("OrderItemORM", back_populates="order")

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
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'email': self.email,
            'phone': self.phone,
            'address_id': self.address_id,
            'order_datetime': self.order_datetime,
            'status': self.status,
            'items_ordered': [item.to_dict() for item in self.items_ordered]
        }
