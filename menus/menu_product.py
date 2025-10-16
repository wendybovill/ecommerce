from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Optional
from functions.product_manager import delete_product, load_products, save_products, add_product, _convert_product_price_from_string, _convert_product_stock, _sorted_product, sort_products
from functions.category_manager import list_categories, add_category
from functions.product_categories import assign_category_to_product_by_code, get_category_menu, assign_category_to_product_by_index, get_category_picker_with_codes, filter_products_by_category_code, filter_products_by_category_id
from env import DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH
from menus.menu_product_sort import sort_products_menu

PRODUCTS_PATH: Path = DEFAULT_PRODUCT_PATH
CATEGORIES_PATH: Path = DEFAULT_CATEGORIES_PATH
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

def product_menu():
    while True:

        print("""\n
+ ========= Product Menu ========= +
|                                  |
| 1) View Products                 |
| 2) Add Product with Category     |
| 3) Change a Product's Category   |
| 4) Delete Product                |
| 5) Sort Products                 |
| 6) Filter Products               |
| 7) Main Menu                     |
|                                  |
+ -------------------------------- +\n
""")
        product_choice = input(">> Please select option (1-4): ").strip()
        if product_choice == "1":
            view_products()
        elif product_choice == "2":
            add_product_with_category_menu()
        elif product_choice == "3":
            change_product_category_menu()
        elif product_choice == "4":
            delete_product_menu()
        elif product_choice == "5":
            sort_products_menu()
        elif product_choice == "6":
            filter_products_by_category_menu()
        elif product_choice == "7":
            return
        else:
            print("* Invalid selection. Please enter a number between 1 and 4.")


def view_products() -> None:
    products = load_products(PRODUCTS_PATH)
    if not products:
        print("\nNo products found.")
        return

    print("\nProducts:")

    for i, product in enumerate(products, start=1):
        name = product.get("name", "(unnamed)")
        category = product.get("category_name") or "-"
        price = product.get("price", 0)
        stock = product.get("stock", 0)
        order_tally = product.get("order_tally", 0)

        price_str = f" | £{price:.2f}" if isinstance(price, (int, float)) else ""
        stock_str = f" | Stock: {stock}" if isinstance(stock, int) else ""
        order_tally_str = f" | Order Tally: {order_tally}" if isinstance(order_tally, int) else ""
        # print(f"  {i}. {name}  | Category: {category}{price_str}{stock_str}{order_tally_str}")

        print(f" ID {i}. | Name: {name}  | Category: {category} | Price: £{price:.2f} | Stock: {stock} | Order Tally: {order_tally}\n")


def _find_product_index_by_id(products: List[Dict], product_id: int) -> int:
    for i, product in enumerate(products):
        try:
            if int(product.get("product_id", -1)) == int(product_id):
                return i
        except (TypeError, ValueError):
            pass
    return -1

def add_product_with_category_menu() -> None:
    name = input("Enter product name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    # prompt for price & description
    price = input("Enter price (e.g., 12.50): ").strip()
    stock = input("Enter stock (e.g., 10): ").strip()

    # convert and validate price
    price_val = _convert_product_price_from_string(price)
    if price_val is None:
        print("Product price is invalid. Please enter a non-negative number (e.g., 12.50).")
        return None

    # convert and validate stock
    stock_val = _convert_product_stock(stock)
    if stock_val is None:
        print("Product stock is invalid. Please enter a non-negative whole number (e.g., 0 or 25).")
        return None

    created = add_product(name, price, stock, path=PRODUCTS_PATH)
    if not created:
        return

    products = load_products(PRODUCTS_PATH)
    product_index = _find_product_index_by_id(products, created["product_id"])
    if product_index < 0:
        print("Unexpected error: new product not found.")
        return

    # Assign category by index or code
    print("\nYou can assign a category by display code (e.g., 10 or 10.2).")
    print("Current category tree:")
    for line in get_category_picker_with_codes(CATEGORIES_PATH):
        print("  " + line)
    raw_code = input("Enter category code (or press Enter to choose from list): ").strip()
    if raw_code:
        if assign_category_to_product_by_code(
            products_index=product_index,
            category_code=raw_code,
            products_path=PRODUCTS_PATH,
            categories_path=CATEGORIES_PATH
        ):
            return
        else:
            print("Could not assign using code; falling back to the list picker.")

    # If categories exist, let user pick; if not, force-create and auto-assign
    categories = list_categories(CATEGORIES_PATH)
    if not categories:
        print("\nNo categories exist yet.")
        while True:
            new_name = input("Create a category for this product: ").strip()
            if not new_name:
                print("Category name cannot be empty.")
                continue
            added = add_category(new_name, path=CATEGORIES_PATH)
            if added:
                products[product_index]["category_id"] = int(added.get("category_id", added.get("id")))
                products[product_index]["category_name"] = added["name"]
                save_products(products, PRODUCTS_PATH)
                print(f"Assigned '{name}' → {added['name']} (id={added.get('category_id', added.get('id'))})")
                return
            print("That category couldn’t be created (maybe it already exists). Try a different name.")
    else:
        lines = get_category_menu(CATEGORIES_PATH, allow_add=True)
        print("\nChoose a category for this product (or press Enter to add a new one):")
        for line in lines:
            print("  " + line)

        raw = input("Enter a number (or press Enter): ").strip()
        if raw == "":
            # User prefers to add a fresh category and auto-assign
            while True:
                new_name = input("Enter new category name: ").strip()
                if not new_name:
                    print("Category name cannot be empty.")
                    continue
                added = add_category(new_name, path=CATEGORIES_PATH)
                if added:
                    products[product_index]["category_id"] = int(added.get("category_id", added.get("id")))
                    products[product_index]["category_name"] = added["name"]
                    save_products(products, PRODUCTS_PATH)
                    print(f"Assigned '{name}' → {added['name']} (id={added.get('category_id', added.get('id'))})")
                    return
                print("That category couldn’t be created (maybe it already exists). Try a different name.")
        else:
            try:
                selected = int(raw)
            except ValueError:
                print("Please enter a valid number.")
                return

            # If the user picked "+ Add a new category…" (last line), collect a name
            new_name = None
            if selected == len(lines):
                new_name = input("Enter new category name: ").strip()
                if not new_name:
                    print("Category name cannot be empty.")
                    return

            ok = assign_category_to_product_by_index(
                products_index=product_index,
                category_selection_index=selected,
                products_path=DEFAULT_PRODUCT_PATH,
                categories_path=DEFAULT_CATEGORIES_PATH,
                new_category_name=new_name,
                allow_add=True,
            )
            if ok:
                print("Product created and category assigned.")
            else:
                print("Could not assign the category. Let’s create one now.")
                while True:
                    new_name = input("Enter new category name: ").strip()
                    if not new_name:
                        print("Category name cannot be empty.")
                        continue
                    added = add_category(new_name, path=CATEGORIES_PATH)
                    if added:
                        products = load_products(PRODUCTS_PATH)  # reload to be safe
                        product_index = _find_product_index_by_id(products, created["product_id"])
                        products[product_index]["category_id"] = int(added.get("category_id", added.get("id")))
                        products[product_index]["category_name"] = added["name"]
                        save_products(products, PRODUCTS_PATH)
                        print(f"Assigned '{name}' → {added['name']} (id={added.get('category_id', added.get('id'))})")
                        return
                    print("That category couldn’t be created (maybe it already exists). Try a different name.")


def change_product_category_menu() -> None:
    products = load_products(PRODUCTS_PATH)
    if not products:
        print("No products found.")
        return

    print("\nChoose a product to change category:")
    for i, product in enumerate(products, start=1):
        category = product.get("category_name") or "-"
        print(f"  {i}. {product.get('name','(unnamed)')}  | Category: {category}")

    raw = input("Pick a product number (or Enter to cancel): ").strip()
    if raw == "":
        return
    try:
        product_index = int(raw) - 1
        if product_index < 0 or product_index >= len(products):
            print("Out of range.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    # If no categories exist, force-create one and auto-assign
    categories = list_categories(CATEGORIES_PATH)
    if not categories:
        print("\nNo categories exist yet.")
        while True:
            new_name = input("Create a category: ").strip()
            if not new_name:
                print("Category name cannot be empty.")
                continue
            added = add_category(new_name, path=CATEGORIES_PATH)
            if added:
                products[product_index]["category_id"] = int(added.get("category_id", added.get("id")))
                products[product_index]["category_name"] = added["name"]
                save_products(products, PRODUCTS_PATH)
                print(f"Assigned '{products[product_index].get('name','(unnamed)')}' → {added['name']}")
                return
            print("That category couldn’t be created (maybe it already exists). Try a different name.")
    else:
        lines = get_category_menu(CATEGORIES_PATH, allow_add=True)
        print("\nChoose a new category:")
        for line in lines:
            print("  " + line)

        try:
            selected = int(input("Enter a number: ").strip())
        except ValueError:
            print("Please enter a valid number.")
            return

        new_name = None
        if selected == len(lines):  # "+ Add a new category…"
            new_name = input("Enter new category name: ").strip()
            if not new_name:
                print("Name cannot be empty.")
                return

        ok = assign_category_to_product_by_index(
            products_index=product_index,
            category_selection_index=selected,
            products_path=PRODUCTS_PATH,
            categories_path=CATEGORIES_PATH,
            new_category_name=new_name,
            allow_add=True,
        )
        if ok:
            print("Product category updated.")
        else:
            print("No category assigned.")


def delete_product_menu() -> None:
    products = load_products(PRODUCTS_PATH)
    if not products:
        print("\nNo products to delete.")
        return

    print("\nProducts:")
    for product in products:
        print(f" [ID {product.get('product_id')}] - {product.get('name','(unnamed)')}")

    raw = input("\n>> Enter the Product ID Number to delete (or Enter to cancel): ").strip()
    if raw == "":
        return
    try:
        pid = int(raw)
    except ValueError:
        print("Please enter a numeric ID.")
        return

    confirm = input(f"Delete product id={pid}? Type DELETE to confirm: ").strip()
    if confirm != "DELETE":
        print("Cancelled.")
        return

    ok = delete_product(pid, products_path=PRODUCTS_PATH)
    if ok:
        print("Product deleted.")
    # delete_product prints reason if blocked by orders


def _fmt_product_line(i: int, product: Dict) -> str:
    name = product.get("name", "(unnamed)")
    category = product.get("category_name") or "-"
    price = product.get("price")
    stock = product.get("stock")
    total_ord = product.get("total_ordered", 0) or 0

    price_str = f" | £{price:.2f}" if isinstance(price, (int, float)) else ""
    stock_str = f" | stock: {stock}" if isinstance(stock, int) else ""
    orders_str = f" | ordered: {int(total_ord)}"
    return f"  {i}. {name} (id={product.get('id')}) | category: {category}{price_str}{stock_str}{orders_str}"


def filter_products_by_category_menu() -> None:
    """
    Filter and display products by a category or subcategory display code.
    Option: include descendants or direct children only.
    """
    print("\nCategory tree (with display codes):")
    for line in get_category_picker_with_codes(CATEGORIES_PATH):
        print("  " + line)

    code = input("\nEnter display code to filter (e.g., 10 or 10.2, or Enter to cancel): ").strip()
    if not code:
        return

    depth = ""
    while depth not in ("1", "2"):
        depth = input("Include: 1) Exact category only  2) Category + ALL subcategories: ").strip()
    include_desc = (depth == "2")

    products, cid = filter_products_by_category_code(
        code,
        include_descendants=include_desc,
        products_path=PRODUCTS_PATH,
        categories_path=CATEGORIES_PATH
    )
    if not products:
        print("\nNo products matched.")
        return

    # Sort nicely by name for display; you can change to id/price/etc if you prefer
    products = sorted(products, key=lambda product: str(product.get("name","")).casefold())
    print(f"\nProducts in category [{code}] (and descendants={include_desc}):")
    for i, product in enumerate(products, start=1):
        name = product.get("name","(unnamed)")
        price = product.get("product_price")
        stock = product.get("product_stock")
        cat = product.get("category_name") or "-"
        orders = int(product.get("product_total_ordered", 0) or 0)
        price_str = f" | £{price:.2f}" if isinstance(price, (int, float)) else ""
        stock_str = f" | stock: {stock}" if isinstance(stock, int) else ""
        print(f"  {i}. {name} (id={product.get('product_id')}) | category: {cat}{price_str}{stock_str} | ordered: {orders}")