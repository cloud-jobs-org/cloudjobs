from flask import Blueprint, render_template, url_for, flash, request, redirect
from pydantic import ValidationError

from src.main import customer_controller, product_controller
from src.database.models.messaging import ContactForm
from src.authentication import user_details
from src.database.models.users import User

home_route = Blueprint('home', __name__)


@home_route.get("/")
@user_details
async def get_home(user: User | None):
    social_url = url_for('home.get_home', _external=True)
    category_list = await product_controller.get_categories()
    context = dict(user=user, social_url=social_url, category_list=category_list)
    return render_template('index.html', **context)


@home_route.get("/about")
@user_details
async def get_about(user: User | None):
    social_url = url_for('home.get_home', _external=True)
    context = dict(user=user, social_url=social_url)
    return render_template('about.html', **context)


@home_route.get("/contact")
@user_details
async def get_contact(user: User | None):
    social_url = url_for('home.get_home', _external=True)
    context = dict(user=user, social_url=social_url)
    return render_template('contact.html', **context)


@home_route.post("/contact")
@user_details
async def send_contact(user: User | None):

    try:
        if not user:
            flash(message="we cannot send a message if you are not logged in please create an account", category="danger")
            return redirect(url_for('home.get_contact'))

        contact_details: ContactForm = ContactForm(**request.form, uid=user.uid)

    except ValidationError as e:
        print(str(e))
        flash(message="please fill in all your contact details", category="danger")
        return redirect(url_for('home.get_contact'))

    saved_contact = await customer_controller.add_update_contact_form(contact_details=contact_details)
    # TODO Send Email with a follow up link

    flash(message="Message successfully to follow up on your query please check your email inbox for details", category="success")
    social_url = url_for('home.get_home', _external=True)
    context = dict(user=user, social_url=social_url)
    return render_template('contact.html', **context)

