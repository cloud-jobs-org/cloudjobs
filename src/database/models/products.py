from enum import Enum
from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel, Field
from src.utils import create_category_id, create_product_id


class InventoryEntryReasons(Enum):
    ADD = "Addition"
    SUBTRACT = "Subtraction"
    SALE = "Sale"  # Added SALE reason
    BREAKAGE = "Breakage"
    STOCK = "Stock"
    REFUND = "Refund"


class InventoryEntries(BaseModel):
    """Inventory of products"""
    entry_id: str
    product_id: str
    amount: int
    entry_datetime: str
    reason: str
    price: int

    @property
    def real_amount(self) -> int:
        if self.reason == InventoryEntryReasons.ADD.value:
            return self.amount
        elif self.reason == InventoryEntryReasons.STOCK.value:
            return self.amount
        elif self.reason == InventoryEntryReasons.SUBTRACT.value:
            return self.amount * -1
        elif self.reason == InventoryEntryReasons.SALE.value:
            return self.amount * -1
        elif self.reason == InventoryEntryReasons.REFUND.value:
            return self.amount

    @property
    def stock_value(self) -> int:
        return self.real_amount * self.price

    @property
    def is_stock_in(self):
        return self.reason in [InventoryEntryReasons.REFUND.value, InventoryEntryReasons.STOCK.value,
                               InventoryEntryReasons.ADD.value]

    @property
    def entry_date(self) -> Date:
        # Convert entry_datetime string to a datetime object
        entry_datetime_obj = datetime.strptime(self.entry_datetime, "%Y-%m-%d %H:%M:%S")
        # Format the datetime object to a date string
        return entry_datetime_obj


class Product(BaseModel):
    """Product being sold"""
    category_id: str
    product_id: str = Field(default_factory=create_product_id)
    name: str
    description: str
    img_link: str | None
    cost_price: int
    sale_price: int
    inventory_entries: list[InventoryEntries] = Field(default_factory=list)

    @property
    def margin(self):
        return self.sale_price - self.cost_price

    @property
    def total_inventory(self):
        return sum([entry.real_amount for entry in self.inventory_entries])

    @property
    def stock_value(self):
        return sum([entry.stock_value for entry in self.inventory_entries])

    def total_stock_count_in_date_range(self, start_date: Date, stop_date: Date):
        """

        :param start_date:
        :param stop_date:
        :return:
        """
        return sum(
            entry.real_amount for entry in self.inventory_entries
            if start_date <= entry.entry_date <= stop_date
        )

    def total_stock_in_value_in_date_range(self, start_date: Date, stop_date: Date):
        """

        :param start_date:
        :param stop_date:
        :return:
        """
        return sum(
            entry.stock_value for entry in self.inventory_entries
            if (start_date <= entry.entry_date <= stop_date) and entry.is_stock_in
        )

    def total_stock_out_value_in_date_range(self, start_date: Date, stop_date: Date):
        """

        :param start_date:
        :param stop_date:
        :return:
        """
        return sum(
            entry.stock_value for entry in self.inventory_entries
            if (start_date <= entry.entry_date <= stop_date) and not entry.is_stock_in
        )


class Category(BaseModel):
    """Product category"""
    category_id: str = Field(default_factory=create_category_id)
    name: str
    description: str
    img_link: str | None
    products_list: list[Product | None] = Field(default_factory=list)
