import random
import string
import uuid


def create_invoice_number() -> str:
    """
    Generate a short invoice number using a combination of letters and numbers.

    The generated invoice number follows the format of three uppercase letters,
    followed by a dash, and a nine-digit number. The letters are randomly selected
    from the uppercase alphabet, and the numbers are generated randomly.

    :return: A string representing the generated invoice number.
    """
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = str(random.randint(0, 999999999)).zfill(9)
    return f"{letters}-{numbers}"


def create_transaction_id() -> str:
    """
    Create a transaction ID.

    :return: A string representing the generated transaction ID.
    """
    return str(uuid.uuid4())
