from flask import Blueprint, render_template, url_for, redirect, flash, request

from src.database.models.contacts import PostalAddress, Address
from src.database.models.orders import Order, OrderItem, OrderStatus
from src.database.models.customers import CustomerDetails
from src.main import customer_controller, product_controller

from src.database.models.products import Product, InventoryEntries, InventoryEntryReasons, Category
from src.authentication import user_details, login_required
from src.database.models.users import User

cart_route = Blueprint('cart', __name__)
from pprint import pprint


@cart_route.get("/shopping-cart")
@user_details
async def get_cart(user: User | None):
    social_url = url_for('cart.get_cart', _external=True)

    # customer_details = await customer_controller.get_customer_details(customer_id=user.customer_id)

    products_list: list[Product] = await product_controller.get_products()
    categories_list: list[Category] = await product_controller.get_categories()

    context = dict(user=user, social_url=social_url, category_list=categories_list, products_list=products_list)
    return render_template('cart/cart.html', **context)


@cart_route.get("/shopping-cart/category/<string:category_name>")
@user_details
async def get_category_products(user: User | None, category_name: str):
    """

    :param user:
    :param category_name:
    :return:
    """
    category_details = await product_controller.get_category_details(category_name=category_name)
    products_list = await product_controller.get_category_products(category_id=category_details.category_id)
    context = dict(user=user, category=category_details, products_list=products_list)
    return render_template('cart/includes/category_products.html', **context)


@cart_route.get("/orders")
@login_required
async def get_orders(user: User | None):
    social_url = url_for('cart.get_orders', _external=True)
    country_list = await customer_controller.get_countries()
    customer_details = await customer_controller.get_customer_details(customer_id=user.customer_id)

    temp_orders: list[Order] = await customer_controller.get_temp_orders(customer_id=user.customer_id)

    context = dict(user=user,
                   country_list=country_list,
                   social_url=social_url,
                   customer=customer_details,
                   current_orders=temp_orders)

    if customer_details and customer_details.postal_id and (customer_details.postal_id == customer_details.delivery_address_id):
        postal_address = await customer_controller.get_postal_address(postal_id=customer_details.postal_id)
        context.update(edit_address=postal_address, postal_address=postal_address, address_type="postal")
        print(f"Postal Address : {postal_address}")
    elif customer_details and customer_details.address_id and (customer_details.address_id == customer_details.delivery_address_id):
        physical_address = await customer_controller.get_address(address_id=customer_details.address_id)
        context.update(edit_address=physical_address, physical_address=physical_address, address_type="physical")
        print(f"Physical Address : {physical_address}")
    else:
        print(f"Why : {customer_details}")
    return render_template('orders/orders.html', **context)


@cart_route.post("/orders/<string:product_id>")
@login_required
async def place_orders(user: User, product_id: str):
    order_quantity = request.form.get('quantity')

    if user.customer_id:
        customer_details: CustomerDetails | None = await customer_controller.get_customer_details(
            customer_id=user.customer_id)
        product_detail: Product | None = await product_controller.get_product(product_id=product_id)

        if customer_details:
            customer_name = f"{customer_details.full_names} {customer_details.surname}"
            email = customer_details.email if customer_details.email else user.email

            temp_order = await customer_controller.get_temp_order(customer_id=user.customer_id)

            if not temp_order:
                temp_order = Order(customer_id=user.customer_id, customer_name=customer_name, email=email,
                                   phone=customer_details.contact_number,
                                   address_id=customer_details.delivery_address_id,
                                   items_ordered=[])

                saved_temp_order = await customer_controller.add_temp_order(order=temp_order)

            order_item = OrderItem(order_id=temp_order.order_id,
                                   product_id=product_id,
                                   product_name=product_detail.name,
                                   price=product_detail.sale_price,
                                   quantity=order_quantity)
            temp_order.items_ordered.append(order_item)
            add_temp_order = await customer_controller.add_temp_order(order=temp_order)
            # add_items_ordered = await customer_controller.add_items_to_temp_order(customer_id=user.customer_id,
            #                                                                       order_id=temp_order.order_id,
            #                                                                       order_item=order_item)
            for order_item in add_temp_order[-1].items_ordered:
                pprint(order_item)
                pprint('-----------------------------------------------------------------------')
            # pprint(f"order: {add_temp_order[-1]}")
        else:

            flash(message="Please Enter Customer Details", category="danger")
            return redirect(url_for('cart.get_orders'))

    flash(message="Order Successfully Captured", category="success")
    return redirect(url_for('cart.get_cart'))


@cart_route.post("/customer/capture")
@login_required
async def capture_customer_details(user: User):
    """

    :param user:
    :return:
    """
    customer_details = CustomerDetails(**request.form, uid=user.uid, customer_id=user.customer_id)
    customer_details_ = await customer_controller.add_customer_details(customer_details=customer_details)
    if customer_details_:
        flash(message="Successfully Captured Customer Details", category="success")
    else:
        flash(message="Unable to save Customer Details", category="danger")
    return redirect(url_for('cart.get_orders'))


@cart_route.post("/customer/capture/delivery_address")
@login_required
async def update_delivery_address(user: User):
    """

    :param user:
    :return:
    """
    address_type = request.form.get("address_type")
    customer_details = await customer_controller.get_customer_details(customer_id=user.customer_id)
    if address_type == "postal":

        postal_address = PostalAddress(**request.form)
        print(f"Setting postal Address: {postal_address}")
        update_postal_address = await customer_controller.add_postal_address(postal_address=postal_address)

        customer_details.postal_id = postal_address.postal_id
        customer_details.delivery_address_id = postal_address.postal_id
    else:
        physical_address = Address(**request.form)
        print(f"Setting physical Address: {physical_address}")
        update_physical_address = await customer_controller.add_update_address(address=physical_address)

        customer_details.address_id = physical_address.address_id
        customer_details.delivery_address_id = physical_address.address_id
    print(f"customer details: {customer_details}")
    customer_details_ = await customer_controller.add_customer_details(customer_details=customer_details)

    flash(message="Successfully Updated Delivery Address Details", category="success")
    return redirect(url_for('cart.get_orders'))


@cart_route.get("/customer/order/edit/<string:order_id>")
@login_required
async def edit_order(user: User, order_id: str):
    """

    :param user:
    :param order_id:
    :return:
    """

    order: Order = await customer_controller.get_temp_order(customer_id=user.customer_id)
    context = dict(user=user, order=order)
    return render_template('orders/modals/edit.html', **context)


@cart_route.post("/customer/order/edit/<string:order_id>")
@login_required
async def update_order(user: User, order_id: str):
    """

    :param user:
    :param order_id:
    :return:
    """
    print(request.form)
    updated_quantities = {}
    for key, value in request.form.items():
        if key.startswith('quantity_'):
            item_id = key.replace('quantity_', '')
            updated_quantities[item_id] = int(value)

    order: Order = await customer_controller.get_temp_order(customer_id=user.customer_id)

    # Update quantities in the order
    for item in order.items_ordered:
        if item.item_id in updated_quantities:
            item.quantity = updated_quantities[item.item_id]
    updated_order = await customer_controller.add_temp_order(order=order)
    if updated_order:
        order = updated_order[-1]
    flash(message="Order Updated", category="success")
    context = dict(user=user, order=order)

    return render_template('orders/modals/edit.html', **context)


@cart_route.get("/customer/order/view/<string:order_id>")
@login_required
async def get_order(user: User, order_id: str):
    """

    :param user:
    :param order_id:
    :return:
    """
    pass


@cart_route.get("/customer/order/finalize/<string:order_id>")
@login_required
async def finalize_order(user: User, order_id: str):
    """
    """
    customer = await customer_controller.get_customer_details(customer_id=user.customer_id)
    order = await customer_controller.get_order_by_order_id(customer_id=user.customer_id, order_id=order_id)

    order = Order(**order.dict())
    order.status = OrderStatus.PENDING.value
    # _stored_order = await customer_controller.store_order_to_database(order=order)
    context = dict(user=user, order=order, customer=customer)
    email_sent = await customer_controller.email_invoice(email_address=order.email, order=order)

    _stored_order = await customer_controller.add_update_order_to_database(order=order)

    if customer.postal_id and customer.delivery_address_id == customer.postal_id:
        postal_address = await  customer_controller.get_postal_address(postal_id=customer.postal_id)
        context.update(address=postal_address)
    elif customer.address_id and customer.delivery_address_id == customer.address_id:
        physical_address = await customer_controller.get_address(address_id=customer.address_id)
        context.update(address=physical_address)
    else:
        context.update(address={})
    return render_template('orders/modals/quotation.html', **context)


@cart_route.get("/customer/invoice/<string:customer_id>/<string:order_id>")
async def public_invoice_link(customer_id: str, order_id: str):
    """
        Accessible with Email Link --
    :param customer_id:
    :param order_id:
    :return:
    """
    customer = await customer_controller.get_customer_details(customer_id=customer_id)
    order = await customer_controller.get_order_by_order_id(customer_id=customer_id, order_id=order_id)

    order = Order(**order.dict())

    context = dict(order=order, customer=customer)

    if customer.postal_id and customer.delivery_address_id == customer.postal_id:
        postal_address = await  customer_controller.get_postal_address(postal_id=customer.postal_id)
        context.update(address=postal_address)
    elif customer.address_id and customer.delivery_address_id == customer.address_id:
        physical_address = await customer_controller.get_address(address_id=customer.address_id)
        context.update(address=physical_address)
    else:
        context.update(address={})
    return render_template('orders/modals/quotation.html', **context)

