from flask import Blueprint, render_template, url_for, request, redirect, flash
from pydantic import ValidationError

from src.database.models.orders import OrderStatus
from src.authentication import admin_login
from src.database.models.products import Product, Category
from src.database.models.users import User
from src.main import product_controller, customer_controller

admin_route = Blueprint('admin', __name__)


async def check_if_name_is_invalid(name: str):
    invalid_names = [
        "category", "categories", "product", "products"
    ]
    if name.lower().strip():
        return name.lower().strip() in invalid_names
    return False


@admin_route.get('/admin/orders')
@admin_login
async def get_orders(user: User):
    """

    :param user:
    :return:
    """
    status = OrderStatus.PENDING.value
    pending_orders = await customer_controller.get_orders_by_status(status=status)
    status = OrderStatus.PROCESSING.value
    processing_orders = await customer_controller.get_orders_by_status(status=status)
    status = OrderStatus.SHIPPED.value
    shipped_orders = await customer_controller.get_orders_by_status(status=status)
    status = OrderStatus.DELIVERED.value
    delivered_orders = await customer_controller.get_orders_by_status(status=status)
    status = OrderStatus.CANCELLED.value
    cancelled_orders = await customer_controller.get_orders_by_status(status=status)
    context = {
        'user': user,
        'orders_by_status': {
            OrderStatus.PENDING.value: pending_orders,
            OrderStatus.PROCESSING.value: processing_orders,
            OrderStatus.SHIPPED.value: shipped_orders,
            OrderStatus.DELIVERED.value: delivered_orders,
            OrderStatus.CANCELLED.value: cancelled_orders
        }
    }

    return render_template('admin/orders/orders.html', **context)


@admin_route.get('/admin/order/<string:customer_id>/<string:order_id>')
@admin_login
async def get_customer_order(user: User, customer_id: str, order_id: str):
    """

    :param customer_id:
    :param user:
    :param order_id:
    :return:
    """
    customer_details = await customer_controller.get_customer_details(customer_id=customer_id)
    order = await customer_controller.customer_order_by_order_id(order_id=order_id)
    print(order)
    context = dict(user=user, customer=customer_details, order=order)
    return render_template('admin/orders/includes/order_detail.html', **context)


@admin_route.get('/admin/customers')
@admin_login
async def get_customers(user: User):
    """

    :param user:
    :return:
    """

    customers_list = await customer_controller.get_all_customers()
    context = dict(user=user, customers_list=customers_list)
    return render_template('admin/customers/customers.html', **context)


@admin_route.get('/admin/customer/<string:customer_id>')
@admin_login
async def edit_customer(user: User, customer_id: str):
    """

    :param user:
    :param customer_id:
    :return:
    """
    customer_details = await customer_controller.get_customer_details(customer_id=customer_id)
    context = dict(user=user, customer=customer_details)
    return render_template('admin/customers/includes/edit.html', **context)


@admin_route.get('/admin/products')
@admin_login
async def get_products(user: User):
    products_list = await product_controller.get_products()
    category_list = await product_controller.get_categories()

    context = dict(user=user, category_list=category_list, products_list=products_list)
    return render_template('admin/products/products.html', **context)


@admin_route.get('/admin/categories')
@admin_login
async def get_categories(user: User):
    """

    :param user:
    :return:
    """
    products_list = await product_controller.get_products()
    category_list = await product_controller.get_categories()

    context = dict(user=user, category_list=category_list, products_list=products_list)
    return render_template('admin/products/categories.html', **context)


@admin_route.post('/admin/categories')
@admin_login
async def add_product_category(user: User):
    """

    :param user:
    :return:
    """
    try:
        category_detail = Category(**request.form)
        image = request.files['image']
        if await check_if_name_is_invalid(name=category_detail.name):
            flash(message="Invalid category Name: {category_detail.name}", category="danger")
            return redirect(url_for('admin.get_categories'))

    except ValidationError as e:
        flash(message="Please include all category details", category="danger")
        return redirect(url_for('admin.get_categories'))
    image_link = await product_controller.save_category_image(category_name=category_detail.name, image=image)
    category_detail.img_link = image_link
    category_ = await product_controller.add_category(category_detail=category_detail)

    flash(message="Category added successfully", category="success")
    return redirect(url_for('admin.get_categories'))


@admin_route.get('/admin/<string:category_name>')
@admin_login
async def get_category_products(user: User, category_name: str):
    """

    :param user:
    :param category_name:
    :return:
    """
    category_details = await product_controller.get_category_details(category_name=category_name)
    products_list = await product_controller.get_category_products(category_id=category_details.category_id)
    context = dict(user=user, category=category_details, products_list=products_list)
    return render_template('admin/products/includes/category_products.html', **context)


@admin_route.post('/admin/<string:category_id>/product')
@admin_login
async def add_category_product(user: User, category_id: str):
    """

    :param user:
    :param category_id:
    :return:
    """
    try:
        product_detail = Product(**request.form, category_id=category_id)
        image = request.files.get('image')
        if await check_if_name_is_invalid(name=product_detail.name):
            flash(message="You cannot name your product: {product_detail.name}", category="danger")
            return redirect(url_for('admin.get_categories'))
        print(f"Product Detail: {product_detail}")
    except ValidationError as e:
        print(str(e))
        flash(message="Please include all product details", category="danger")
        return redirect(url_for('admin.get_categories'))

    # TODO - add product image first
    image_link = await product_controller.add_product_image(category_id=category_id, product_name=product_detail.name,
                                                            image=image)
    product_detail.img_link = image_link
    print(f"Updated Product Detail: {product_detail}")
    product = await product_controller.add_category_product(category_id=category_id, product=product_detail)

    flash(message="Successfully Added your product to category", category="success")
    return redirect(url_for('admin.get_categories'))


@admin_route.get('/admin/messages')
@admin_login
async def get_messages(user: User):
    """

    :param user:
    :return:
    """
    contact_messages = await customer_controller.get_all_unresolved_issues()
    context = dict(user=user, contact_messages=contact_messages)
    return render_template('admin/messages/messages.html', **context)


@admin_route.get('/admin/message/<string:contact_id>')
@admin_login
async def get_contact_message(user: User, contact_id: str):
    """

    :param user:
    :param contact_id:
    :return:
    """
    contact_message = await customer_controller.get_contact_message(contact_id=contact_id)
    context = dict(user=user, contact_message=contact_message)

    return render_template('admin/messages/includes/message.html', **context)


@admin_route.post('/admin/message/<string:contact_id>')
@admin_login
async def send_contact_message_response(user: User, contact_id: str):
    """

    :param user:
    :param contact_id:
    :return:
    """

    contact_message = await customer_controller.get_contact_message(contact_id=contact_id)
    flash(message=f"Response is Successfully sent to : contact message : {contact_message.email}", category="success")
    return redirect(url_for("admin.get_contact_message", contact_id=contact_id))