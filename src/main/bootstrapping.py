
def bootstrapper():
    from src.database.sql.user import UserORM,  PayPalORM
    from src.database.sql.bank_account import BankAccountORM
    from src.database.sql.contacts import AddressORM, PostalAddressORM, ContactsORM
    from src.database.sql.customer import CustomerDetailsORM
    from src.database.sql.orders import OrderORM, OrderItemORM
    from src.database.sql.products import CategoryORM, ProductsORM, InventoryEntriesORM

    classes_to_create = [UserORM, PayPalORM, BankAccountORM, AddressORM, PostalAddressORM, ContactsORM,
                         CustomerDetailsORM, OrderORM, OrderItemORM, CategoryORM, ProductsORM, InventoryEntriesORM]

    for cls in classes_to_create:
        cls.create_if_not_table()
