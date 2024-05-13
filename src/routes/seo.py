from flask import Blueprint, render_template, url_for, flash, request, redirect
from pydantic import ValidationError

from src.main import customer_controller, product_controller
from src.database.models.messaging import ContactForm
from src.authentication import user_details
from src.database.models.users import User

seo_route = Blueprint('seo', __name__)


@seo_route.get('/sitemap.xml')
async def get_sitemap():
    return render_template('sitemap.xml')


@seo_route.get('/robots.txt')
async def get_sitemap():
    return render_template('robots.txt')

