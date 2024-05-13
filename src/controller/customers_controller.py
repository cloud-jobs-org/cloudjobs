from flask import Flask, url_for
from sqlalchemy.exc import OperationalError

from src.database.models.messaging import ContactForm
from src.database.sql.messaging import ContactFormORM
from src.emailer import EmailModel
from src.database.sql.orders import OrderORM, OrderItemORM
from src.controller import Controllers, error_handler
from src.database.models.contacts import Address, PostalAddress, Contacts
from src.database.models.customers import CustomerDetails
from src.database.models.orders import Order, OrderStatus, OrderItem
from src.database.sql.contacts import AddressORM, PostalAddressORM, ContactsORM
from src.database.sql.customer import CustomerDetailsORM
from src.main import send_mail


class CustomerController(Controllers):

    def __init__(self):
        super().__init__()

        self.countries = [
            "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde",
            "Cameroon", "Central African Republic", "Chad", "Comoros",
            "Democratic Republic of the Congo", "Republic of the Congo", "Djibouti",
            "Equatorial Guinea", "Eritrea", "Ethiopia", "Gabon", "Gambia", "Ghana",
            "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia",
            "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Mozambique",
            "Namibia", "Niger", "Nigeria", "Rwanda", "Sao Tome and Principe",
            "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa",
            "South Sudan", "Sudan", "Swaziland", "Tanzania", "Togo", "Uganda",
            "Zambia", "Zimbabwe"
        ]

        self.temp_cart_items: dict[str: list[Order]] = {}

    def init_app(self, app: Flask):
        super().init_app(app=app)

    async def add_temp_order(self, order: Order):
        temp_orders_list: list[Order] = self.temp_cart_items.get(order.customer_id, [])
        order_merged = False
        if not temp_orders_list:
            self.temp_cart_items[order.customer_id] = [order]
        else:
            for order_ in temp_orders_list.copy():
                if order_.order_id == order.order_id:
                    temp_orders_list.remove(order_)
                    temp_orders_list.append(order)
                    self.temp_cart_items[order.customer_id] = temp_orders_list
                    break
        return self.temp_cart_items[order.customer_id]

    async def get_temp_orders(self, customer_id: str) -> list[Order]:
        """
        **get_temp_order**

        :param customer_id:
        :return:
        """
        return self.temp_cart_items.get(customer_id, [])

    async def get_temp_order(self, customer_id: str) -> Order:
        """

        :param customer_id:
        :return:
        """
        if self.temp_cart_items.get(customer_id, []):
            return self.temp_cart_items.get(customer_id, [])[-1]
        return None

    async def get_order_by_order_id(self, customer_id: str, order_id: str):
        """

        :param customer_id:
        :param order_id:
        :return:
        """
        orders_list: list[Order] = self.temp_cart_items[customer_id]
        for order in orders_list:
            if order.order_id == order_id:
                return order

    async def add_items_to_temp_order(self, customer_id: str, order_id: str, order_item: OrderItem):
        """

        :param customer_id:
        :param order_id:
        :param order_item:
        :return:
        """
        temp_orders_list: Order | list[Order] = self.temp_cart_items.get(customer_id, [])
        for order in temp_orders_list.copy():
            if order.order_id == order_id:
                temp_orders_list.remove(order)
                order.items_ordered.append(order_item)
                temp_orders_list.append(order)
        self.temp_cart_items[customer_id] = temp_orders_list
        return temp_orders_list

    async def remove_items_from_temp_order(self, customer_id: str, order_id: str, item_id: str):
        temp_orders_list: Order | list[Order] = self.temp_cart_items.get(customer_id, [])
        for order in temp_orders_list.copy():
            if order.order_id == order_id:
                new_items_ordered = []
                for item_ordered in order.items_ordered:
                    if not (item_ordered.item_id == item_id):
                        new_items_ordered.append(item_ordered)
                order.items_ordered = new_items_ordered
                temp_orders_list.remove(order)
                temp_orders_list.append(order)

        self.temp_cart_items[customer_id] = temp_orders_list

    async def remove_order_from_temp(self, order: Order):
        temp_orders_list: Order | list[Order] = self.temp_cart_items.get(order.customer_id, [])
        for order_ in temp_orders_list.copy():
            if order_ == order:
                temp_orders_list.remove(order)
                self.temp_cart_items[order.customer_id] = temp_orders_list

    # noinspection DuplicatedCode
    async def add_customer_details(self, customer_details: CustomerDetails):
        with self.get_session() as session:
            # Query the database for the customer details
            customer_orm = session.query(CustomerDetailsORM).filter_by(customer_id=customer_details.customer_id).first()

            if customer_orm:
                # Update the existing customer details

                customer_orm.customer_id = customer_details.customer_id
                customer_orm.uid = customer_details.uid
                if customer_details.full_names:
                    customer_orm.full_names = customer_details.full_names
                if customer_details.surname:
                    customer_orm.surname = customer_details.surname
                if customer_details.email:
                    customer_orm.email = customer_details.email
                if customer_details.contact_number:
                    customer_orm.contact_number = customer_details.contact_number
                if customer_details.delivery_address_id:
                    customer_orm.delivery_address_id = customer_details.delivery_address_id
                if customer_details.date_joined:
                    customer_orm.date_joined = customer_details.date_joined
                if customer_details.is_active:
                    customer_orm.is_active = customer_details.is_active
                if customer_details.address_id:
                    customer_orm.address_id = customer_details.address_id
                if customer_details.contact_id:
                    customer_orm.contact_id = customer_details.contact_id
                if customer_details.postal_id:
                    customer_orm.postal_id = customer_details.postal_id
                if customer_details.bank_account_id:
                    customer_orm.bank_account_id = customer_details.bank_account_id

            else:
                # Create a new customer entry

                customer_orm = CustomerDetailsORM(
                    customer_id=customer_details.customer_id,
                    uid=customer_details.uid,
                    full_names=customer_details.full_names,
                    surname=customer_details.surname,
                    email=customer_details.email,
                    contact_number=customer_details.contact_number,

                    date_joined=customer_details.date_joined,
                    is_active=customer_details.is_active,
                    delivery_address_id=customer_details.delivery_address_id,
                    address_id=customer_details.address_id,
                    contact_id=customer_details.contact_id,
                    postal_id=customer_details.postal_id,
                    bank_account_id=customer_details.bank_account_id
                )
                session.add(customer_orm)

            session.commit()
            return customer_details


    async def get_customer_details(self, customer_id: str) -> CustomerDetails | None:
        with self.get_session() as session:
            customer_orm: CustomerDetailsORM = session.query(
                CustomerDetailsORM).filter_by(customer_id=customer_id).first()

            if isinstance(customer_orm, CustomerDetailsORM):
                return CustomerDetails(**customer_orm.to_dict())
            return None

    async def get_all_customers(self) -> list[CustomerDetails]:
        """

        :return:
        """
        with self.get_session() as session:
            customers_orm_list = session.query(CustomerDetailsORM).all()
            return [CustomerDetails(**cust_orm.to_dict()) for cust_orm in customers_orm_list]

    # noinspection DuplicatedCode
    @error_handler
    async def add_update_address(self, address: Address) -> Address | None:
        """
        **add_update_address**

        :param address:
        :return:
        """
        with self.get_session() as session:

            address_orm: AddressORM = session.query(AddressORM).filter_by(address_id=address.address_id).first()

            if isinstance(address_orm, AddressORM):

                if address.address_line_1:
                    address_orm.street = address.address_line_1
                if address.town_city:
                    address_orm.town_city = address.town_city
                if address.province:
                    address_orm.province = address.province
                if address.postal_code:
                    address_orm.postal_code = address.postal_code
                if address.country:
                    address_orm.country = address.country

                session.commit()
                return address
            try:
                session.add(AddressORM(**address.dict()))
                session.commit()
                return address
            except OperationalError as e:
                print(str(e))
                return None

    @error_handler
    async def get_address(self, address_id: str) -> Address | None:
        with self.get_session() as session:
            branch_address = session.query(AddressORM).filter_by(address_id=address_id).first()
            if isinstance(branch_address, AddressORM):
                return Address(**branch_address.to_dict())
            return None

    # noinspection DuplicatedCode
    @error_handler
    async def add_postal_address(self, postal_address: PostalAddress) -> PostalAddress | None:
        """

        :param postal_address:
        :return:
        """
        with self.get_session() as session:

            _postal_id = postal_address.postal_id
            postal_orm = session.query(PostalAddressORM).filter_by(postal_id=_postal_id).first()

            if isinstance(postal_orm, PostalAddressORM):
                if postal_address.address_line_1:
                    postal_orm.address_line_1 = postal_address.address_line_1
                if postal_address.town_city:
                    postal_orm.town_city = postal_address.town_city
                if postal_address.province:
                    postal_orm.province = postal_address.province
                if postal_address.country:
                    postal_orm.country = postal_address.country
                if postal_address.postal_code:
                    postal_orm.postal_code = postal_address.postal_code
            else:
                postal_orm = PostalAddressORM(**postal_address.dict())
                session.add(postal_orm)

            session.commit()
            return postal_address

    @error_handler
    async def get_postal_address(self, postal_id: str) -> PostalAddress | None:
        """

        :param postal_id:
        :return:
        """
        with self.get_session() as session:
            postal_address_orm = session.query(PostalAddressORM).filter_by(postal_id=postal_id).first()
            if isinstance(postal_address_orm, PostalAddressORM):
                return PostalAddress(**postal_address_orm.to_dict())
            return None

    # noinspection DuplicatedCode
    @error_handler
    async def add_contacts(self, contact: Contacts) -> Contacts | None:
        """
        Add branch contacts to the database.

        :param contact: Instance of Contacts containing contact details.
        :return: Added Contacts instance if successful, None otherwise.
        """
        with self.get_session() as session:
            contact_orm = session.query(ContactsORM).filter_by(contact_id=contact.contact_id).first()
            if isinstance(contact_orm, ContactsORM):
                # Update existing contact details
                if contact.cell:
                    contact_orm.cell = contact.cell
                if contact.tel:
                    contact_orm.tel = contact.tel
                if contact.email:
                    contact_orm.email = contact.email
                if contact.facebook:
                    contact_orm.facebook = contact.facebook
                if contact.twitter:
                    contact_orm.twitter = contact.twitter
                if contact.whatsapp:
                    contact_orm.whatsapp = contact.whatsapp
                session.commit()
                return contact
            # Add new contact details
            session.add(ContactsORM(**contact.dict()))
            session.commit()
            return contact

    @error_handler
    async def get_contact(self, contact_id: str) -> Contacts | None:
        """
        Retrieve branch contact details from the database.

        :param contact_id: The ID of the branch whose contact details to retrieve.
        :return: Contacts instance if found, None otherwise.
        """
        with self.get_session() as session:
            # Query the database for the contact details associated with the given branch_id
            branch_contact_orm = session.query(ContactsORM).filter_by(contact_id=contact_id).first()

            if isinstance(branch_contact_orm, ContactsORM):
                # If contact details exist, create a Contacts instance from the retrieved data
                branch_contact = Contacts(**branch_contact_orm.to_dict())
                return branch_contact

            return None

    @error_handler
    async def get_countries(self):
        return self.countries

    async def add_update_order_to_database(self, order: Order) -> Order:
        """

        :param order:
        :return:
        """
        with self.get_session() as session:
            order_orm = session.query(OrderORM).filter_by(order_id=order.order_id).first()
            if isinstance(order_orm, OrderORM):
                order_orm.customer_name = order.customer_name
                order_orm.email = order.email
                order_orm.phone = order.phone
                order_orm.address_id = order.address_id
                order_orm.order_datetime = order.order_datetime
                order_orm.status = order.status

                for order_item in order.items_ordered:
                    order_item_orm: OrderItemORM = session.query(OrderItemORM).get(order_item.item_id)
                    if isinstance(order_item_orm, OrderItemORM):
                        order_item_orm.price = order_item.price
                        order_item_orm.product_id = order_item.product_id
                        order_item_orm.product_name = order_item.product_name
                        order_item_orm.quantity = order_item.quantity
                        order_item_orm.discount_percent = order_item.discount_percent
                    else:
                        order_item_orm: OrderItemORM = OrderItemORM(**order_item.dict())
                        session.add(order_item_orm)

            else:
                order_orm_dict = {k: v for k, v in order.dict().items() if k != 'items_ordered'}
                order_orm = OrderORM(**order_orm_dict)
                session.add(order_orm)
                for order_item in order.items_ordered:
                    order_item_orm: OrderItemORM = OrderItemORM(**order_item.dict())
                    session.add(order_item_orm)

            session.commit()
            return order

    async def get_orders_by_status(self, status: str) -> list[Order]:
        """
            class OrderStatus(Enum):
                INCOMPLETE = "Incomplete"
                PENDING = 'Pending'
                PROCESSING = 'Processing'
                SHIPPED = 'Shipped'
                DELIVERED = 'Delivered'
                CANCELLED = 'Cancelled'

        :param status:
        :return:
        """
        with self.get_session() as session:
            orders_list = session.query(OrderORM).filter_by(status=status).all()
            return [Order(**order_orm.to_dict()) for order_orm in orders_list if isinstance(order_orm, OrderORM)]

    async def customer_order_by_order_id(self, order_id: str) -> Order:
        """

        :param order_id:
        :return:
        """
        with self.get_session() as session:
            order_orm = session.query(OrderORM).get(order_id)
            return Order(**order_orm.to_dict())

    async def email_invoice(self, email_address: str, order: Order):
        """

        :param email_address:
        :param order:
        :return:
        """
        invoice_link = url_for('cart.public_invoice_link', customer_id=order.customer_id, order_id=order.order_id,
                               _external=True)
        html = f"""
            <h3 class="card-title">Zwavhudivhudi Trading Pty LTD</h3>


            <h5>Invoice Number: {order.order_id}
            <h5>Sub Total : R {order.total_price}.00</h5>
            <h5>Discount : R {order.total_discount}.00</h5>
            <h5>Total Payable: R {order.total_price - order.total_discount}.00</h5>
            
            <h6>For your Complete Invoice please click below</h6>
            
            <a class="btn btn-sm btn-rounded btn-success" href="{invoice_link}" target="_blank">open invoice</a>
            
            <h6>Thank you</h6>
                <p>Zwavhudivhudi Trading Pty LTD</p>
                <p>Managing Director: Pfunzo Matodzi</p>
                <p>Contact : 079 532 7660</p>
                <p>Email : pfunzo@zwavhudivhudi-electrical.work
                <p>Website : https://zwavhudivhudi-electrical.work</p>
        """
        email = EmailModel(to_=email_address,
                           subject_=f"Zwavhudivhudi Trading - Invoice : {order.order_id}",
                           html_=html)
        await send_mail.send_mail_resend(email=email)
        return email

    async def add_update_contact_form(self, contact_details: ContactForm):
        """

        :param contact_details:
        :return:
        """
        with self.get_session() as session:
            contact_orm = ContactFormORM(**contact_details.dict())
            session.add(contact_orm)
            session.commit()
            return contact_details

    async def get_all_unresolved_issues(self):
        with self.get_session() as session:
            contact_form_list = session.query(ContactFormORM).filter_by(issue_resolved=False).all()
            return [ContactForm(**contact_orn.to_dict()) for contact_orn in contact_form_list
                    if isinstance(contact_orn, ContactFormORM)]

    async def get_contact_message(self, contact_id: str) -> ContactForm:
        """

        :param contact_id:
        :return:
        """
        with self.get_session() as session:
            contact_message_orm = session.query(ContactFormORM).filter_by(contact_id=contact_id).first()
            if isinstance(contact_message_orm, ContactFormORM):
                return ContactForm(**contact_message_orm.to_dict())
            return None