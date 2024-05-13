import uuid, random, string
from enum import Enum
from os import path
from datetime import datetime, timedelta


# TODO create a class to contain this enum types for the entire project
class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    CASH = "cash"
    DIRECT_DEPOSIT = "direct_deposit"
    BANK_TRANSFER = "bank_transfer"


def get_payment_methods() -> list[str]:
    """
    Get a list of payment methods.

    :return: A list of payment methods.
    """
    return [method.value for method in PaymentMethod]


def static_folder() -> str:
    return path.join(path.dirname(path.abspath(__file__)), '../../static')


def template_folder() -> str:
    return path.join(path.dirname(path.abspath(__file__)), '../../templates')


def format_with_grouping(number):
    parts = str(number).split(".")
    whole_part = parts[0]

    formatted_whole_part = ""
    while whole_part:
        formatted_whole_part = whole_part[-3:] + formatted_whole_part
        whole_part = whole_part[:-3]
        if whole_part:
            formatted_whole_part = "," + formatted_whole_part

    if len(parts) > 1:
        decimal_part = parts[1]
        formatted_number = f"{formatted_whole_part}.{decimal_part}"
    else:
        formatted_number = formatted_whole_part

    return formatted_number


def days_left(value):
    if value is None:
        return None

    if value < 60:
        return f"{value} days"
    elif 2 <= value // 30 <= 24:
        months = value // 30
        days = value % 30
        return f"{months} months and {days} days"
    else:
        years = value // 365
        months = (value % 365) // 30
        days = (value % 365) % 30
        return f"{years} years, {months} months, and {days} days"


def format_square_meters(value):
    return f"{value} m²"


def format_payment_method(value):
    if value in [method.value for method in PaymentMethod]:
        return value.replace("_", " ").title()
    else:
        return "Unknown"


def friendlytimestamp(value):
    # Convert the string timestamp to a datetime object
    timestamp_dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')

    # Get the current date and time
    current_dt = datetime.now()

    # Calculate the difference between the timestamps
    time_difference = current_dt - timestamp_dt

    if time_difference.total_seconds() < 60:
        return "just now"
    elif time_difference.total_seconds() < 3600:
        minutes = int(time_difference.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif time_difference.total_seconds() < 86400:
        hours = int(time_difference.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif current_dt.date() == timestamp_dt.date():
        return "today"
    elif current_dt.date() - timestamp_dt.date() == timedelta(days=1):
        return "yesterday"
    elif time_difference.days < 7:
        return f"{time_difference.days} day{'s' if time_difference.days > 1 else ''} ago"
    elif time_difference.days < 30:
        weeks = int(time_difference.days / 7)
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    else:
        return timestamp_dt.strftime("%Y-%m-%d")


def create_id():
    return str(uuid.uuid4())


def create_plan_number():
    # Generate a random alphanumeric string of length 9
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
    # Convert all letters to uppercase
    random_chars_uppercase = random_chars.upper()
    return random_chars_uppercase


def create_claim_number():
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
    random_chars_uppercase = random_chars.upper()
    return random_chars_uppercase


def create_policy_number():
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    random_chars_uppercase = random_chars.upper()
    return random_chars_uppercase


def create_customer_id():
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    random_chars_uppercase = random_chars.upper()
    return random_chars_uppercase


def create_category_id():
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    random_chars_uppercase = random_chars.upper()
    return random_chars_uppercase
def create_product_id():
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    random_chars_uppercase = random_chars.upper()
    return random_chars_uppercase

def create_order_number():
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    random_chars_uppercase = random_chars.upper()
    return random_chars_uppercase


def string_today():
    return str(datetime.today().date())
