from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Optional
from functions.product_manager import delete_product, load_products, save_products, add_product, _convert_product_price_from_string, _convert_product_stock, _sorted_product, _fmt_product_line
from functions.category_manager import list_categories, add_category, update_category_name, delete_category
from functions.product_categories import get_category_menu, assign_category_to_product_by_index, apply_category_choice_to_product
from env import DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH

PRODUCTS_PATH: Path = DEFAULT_PRODUCT_PATH        # data_files/product_catelog.json
CATEGORIES_PATH: Path = DEFAULT_CATEGORIES_PATH  # data_files/category_catelog.json

class Product:
    """
    The product name is a required field.
    Id is auto-generated.
    """

    def __init__(self, name, category, price, stock ):
        self.id = None  # to be set when saved
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'products'

def sort_products_menu():
    """
    Sort by: ID, Name, Price, Ordered total, Stock; ask for direction.
    """
    while True:

        print("""\n
+ ======= Product Sort Menu ======= +
|                                   |
| 1) Sort by ID                     |
| 2) Sort by Name                   |
| 3) Sort by Price                  |
| 4) Sort by Product Totals Ordered |
| 5) Sort by Orders                 |
| 6) Main Menu                      |
|                                   |
+ --------------------------------- +\n
""")
        sort_choice = input(">> Select field to sort by: ").strip()
        if sort_choice == "6" or sort_choice == "":
            return

        by_map = {
            "1": "id",
            "2": "name",
            "3": "price",
            "4": "orders",
            "5": "stock",
        }
        by = by_map.get(sort_choice)
        if not by:
            print("Invalid Selection. Select Numbers 1 to 5, or Enter to cancel and return to Product Menu.")
            return

        direction = ""
        while direction not in ("asc", "desc"):
            direction = input("Direction [asc/desc]: ").strip().lower()

        sorted_list = _sorted_product(by=by, direction=direction)
        if not sorted_list:
            print("\nNo products found.")
            return

        print(f"\nSorted by {by} ({direction}):")
        for i, product in enumerate(sorted_list, start=1):
            print(_fmt_product_line(i, product))

