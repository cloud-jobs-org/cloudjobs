from flask import Flask

from src.database.models.orders import Order, OrderItem, OrderStatus
from src.controller import Controllers
from src.database.sql.orders import OrderORM, OrderItemORM


class OrdersController(Controllers):
    def __init__(self):
        super().__init__()

    def init_app(self, app: Flask):
        """

        :param app:
        :return:
        """
        super().init_app(app=app)

    async def return_customer_orders(self, customer_id: str) -> list[Order]:
        """

        :param customer_id:
        :return:
        """
        with self.get_session() as session:
            customers_orders = session.query(OrderORM).filter_by(customer_id=customer_id).all()
            return [Order(**order_orm.to_dict()) for order_orm in customers_orders if isinstance(order_orm, customers_orders)]

    async def add_order(self, order: Order) -> Order | None:
        """
        Add or update an order.

        :param order: Order object.
        :return: Order object if added or updated successfully, None otherwise.
        """
        with self.get_session() as session:
            # Check if order exists
            order_orm = session.query(OrderORM).filter_by(order_id=order.order_id).first()
            if order_orm:
                # Order exists, update it
                order_orm.customer_id = order.customer_id
                order_orm.customer_name = order.customer_name
                order_orm.email = order.email
                order_orm.phone = order.phone
                order_orm.address_id = order.address_id
                order_orm.order_datetime = order.order_datetime
                order_orm.status = order.status
                # You may need to handle items_ordered separately depending on your implementation
                # For example, you may want to delete existing items and add new ones
                # Or you may want to update existing items and add new ones
            else:
                # Order does not exist, create a new one
                order_orm = OrderORM(
                    order_id=order.order_id,
                    customer_id=order.customer_id,
                    customer_name=order.customer_name,
                    email=order.email,
                    phone=order.phone,
                    address_id=order.address_id,
                    order_datetime=order.order_datetime,
                    status=order.status
                )
                session.add(order_orm)

            # Commit changes
            session.commit()

            # Return the updated or new order
            return order

    async def get_order_by_order_id(self, order_id: str) -> Order | None:
        """

        :param order_id:
        :return:
        """
        with self.get_session() as session:
            order_orm = session.query(OrderORM).filter_by(order_id=order_id).first()
            if isinstance(order_orm, OrderORM):
                return Order(**order_orm.to_dict())
            return None

    async def add_order_item(self, item: OrderItem) -> bool:
        """
        Add an order item to an existing order.

        :param order_id: ID of the order.
        :param item: OrderItem object to add.
        :return: True if added successfully, False otherwise.
        """
        with self.get_session() as session:
            # Check if order exists
            order_orm = session.query(OrderORM).filter_by(order_id=item.order_id).first()
            if not order_orm:
                return False

            # Create OrderItemsORM object
            order_item_orm = OrderItemORM(
                order_id=item.order_id,
                product_id=item.product_id,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity,
                discount_percent=item.discount_percent
            )

            # Add to database
            session.add(order_item_orm)
            session.commit()
            return True

    async def remove_order_item(self, item_id: str) -> bool:
        """
        Remove an order item.

        :param item_id: ID of the item to remove.
        :return: True if removed successfully, False otherwise.
        """
        with self.get_session() as session:
            # Retrieve order item
            order_item_orm = session.query(OrderItemORM).filter_by(item_id=item_id).first()
            if not order_item_orm:
                return False

            # Remove from database
            session.delete(order_item_orm)
            session.commit()
            return True

    async def return_pending_orders(self):
        with self.get_session() as sessioo:
            pending_orders = sessioo.query(OrderORM).filter_by(status=OrderStatus.PENDING.value).all()
            return [Order(**order_orm.to_dict()) for order_orm in pending_orders if isinstance(order_orm, OrderORM)]

    async def return_cancelled_orders(self):
        """

        :return:
        """
        with self.get_session() as sessioo:
            pending_orders = sessioo.query(OrderORM).filter_by(status=OrderStatus.CANCELLED.value).all()
            return [Order(**order_orm.to_dict()) for order_orm in pending_orders if isinstance(order_orm, OrderORM)]

    async def return_delivered_orders(self):
        with self.get_session() as sessioo:
            pending_orders = sessioo.query(OrderORM).filter_by(status=OrderStatus.DELIVERED.value).all()
            return [Order(**order_orm.to_dict()) for order_orm in pending_orders if isinstance(order_orm, OrderORM)]

    async def return_shipped_orders(self):
        with self.get_session() as sessioo:
            pending_orders = sessioo.query(OrderORM).filter_by(status=OrderStatus.SHIPPED.value).all()
            return [Order(**order_orm.to_dict()) for order_orm in pending_orders if isinstance(order_orm, OrderORM)]

    async def return_orders_in_processing(self):
        with self.get_session() as sessioo:
            pending_orders = sessioo.query(OrderORM).filter_by(status=OrderStatus.PROCESSING.value).all()
            return [Order(**order_orm.to_dict()) for order_orm in pending_orders if isinstance(order_orm, OrderORM)]
