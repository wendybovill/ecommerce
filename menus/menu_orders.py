from pathlib import Path
from typing import List, Dict
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Optional
from env import DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH, DEFAULT_CUSTOMER_PATH
from functions.product_manager import delete_product, load_products, save_products, add_product, _convert_product_price_from_string, _convert_product_stock, _sorted_product, sort_products
from functions.category_manager import list_categories, add_category
from functions.product_categories import get_category_menu, assign_category_to_product_by_index
from functions.order_manager import add_order, edit_order, delete_order, list_orders, DEFAULT_ORDER_PATH
from menus.menu_product_sort import sort_products_menu


ORDERS_PATH: Path = DEFAULT_ORDER_PATH
PRODUCT_PATH: Path = DEFAULT_PRODUCT_PATH
CUSTOMER_PATH: Path = DEFAULT_CUSTOMER_PATH
CATEGORY_PATH: Path = DEFAULT_CATEGORIES_PATH


def _pick_customer_id() -> int:
    customers = list_customers_sorted(DEFAULT_CUSTOMER_PATH)
    if not customers:
        print("No customers. Please add a customer first.")
        return -1
    print("\nCustomers:")
    for c in customers:
        print(f"  id={c.get('customer_id')}: {c.get('first_name','')} {c.get('last_name','')} | {c.get('email','')}")
    raw = input("Enter customer ID (or Enter to cancel): ").strip()
    if raw == "":
        return -1
    try:
        return int(raw)
    except ValueError:
        print("Please enter a numeric ID.")
        return -1

def _pick_product(items_accum: List[Dict]) -> bool:
    """
    Add one product+qty into items_accum.
    Returns False if user finished; True if an item was added or retry needed.
    """
    products = load_products(PRODUCT_PATH)
    if not products:
        print("No products available.")
        return False

    print("\nProducts:")
    for i, product in enumerate(products, start=1):
        price = product.get("price", 0)
        stock = product.get("stock", 0)
        print(f"  {i}. {product.get('name','(unnamed)')} (id={product.get('product_id')}) | £{price:.2f} | stock {stock}")

    raw = input(">> Pick a product number (or Enter to finish): ").strip()
    if raw == "":
        return False
    try:
        index = int(raw) - 1
    except ValueError:
        print("Please enter a valid number.")
        return True

    if index < 0 or index >= len(products):
        print("Out of range.")
        return True

    product = products[index]
    qty_raw = input(f"Enter quantity for '{product.get('name','(unnamed)')}' (>=1): ").strip()
    try:
        qty = int(qty_raw)
        if qty <= 0:
            raise ValueError
    except ValueError:
        print("Quantity must be a positive whole number.")
        return True

    items_accum.append({"product_id": int(product.get("product_id")), "qty": qty})
    unit_price = float(product.get("price", 0.0) or 0.0)
    print(f"  Added: id={product.get('product_id')} x {qty} @ £{unit_price:.2f}  |  Subtotal £{unit_price*qty:.2f}")
    return True

def _preview_basket(items: List[Dict]) -> None:
    if not items:
        print("\nBasket: (empty)")
        return
    print("\nBasket:")
    products = {int(product["product_id"]): product for product in load_products(PRODUCTS_PATH)}
    total = 0.0
    for it in items:
        pid, qty = it["product_id"], it["qty"]
        p = products.get(int(pid))
        name = p.get("name","") if p else f"(id {pid})"
        unit = float(p.get("price", 0.0) or 0.0) if p else 0.0
        sub = round(unit * qty, 2)
        total = round(total + sub, 2)
        print(f"  - {name} (id={pid})  x{qty}  |  Price £{unit:.2f}  |  Subtotal £{sub:.2f}")
    print(f"Order Total: £{total:.2f}")

def create_order_menu() -> None:
    cid = _pick_customer_id()
    if cid <= 0:
        return

    items: List[Dict] = []
    print("\nAdd items (pick from list, then enter quantity).")
    while _pick_product(items):
        pass

    if not items:
        print("No items added. Cancelled.")
        return

    _preview_basket(items)
    confirm = input(">> Place order? Type YES to confirm: ").strip()
    if confirm != "YES":
        print("Cancelled.")
        return

    order = add_order(items, customer_id=cid)
    if not order:
        return

def _list_orders_basic() -> List[Dict]:
    orders = list_orders()
    if not orders:
        print("\nNo orders.")
        return []
    print("\nOrders (most recent first):")
    for o in orders:
        print(f"  - #{o.get('order_id')} | uuid {o.get('order_uuid')} | customer #{o.get('customer_id')} | £{o.get('order_total',0):.2f} | {o.get('created_at')}")
    return orders

def edit_order_menu() -> None:
    orders = _list_orders_basic()
    if not orders:
        return
    raw = input(">> Enter order ID to edit (or Enter to cancel): ").strip()
    if raw == "":
        return
    try:
        oid = int(raw)
    except ValueError:
        print("Please enter a numeric ID.")
        return

    print("\nRebuild the basket for this order:")
    items: List[Dict] = []
    while _pick_product(items):
        pass
    if not items:
        print("No items provided. Cancelled.")
        return

    _preview_basket(items)
    confirm = input(">> Save changes? Type YES to confirm: ").strip()
    if confirm != "YES":
        print("Cancelled.")
        return

    edited = edit_order(oid, items)
    if edited:
        print(f"Order #{oid} updated.")

def delete_order_menu() -> None:
    orders = _list_orders_basic()
    if not orders:
        return
    raw = input(">> Enter order ID to delete (or Enter to cancel): ").strip()
    if raw == "":
        return
    try:
        oid = int(raw)
    except ValueError:
        print("Please enter a numeric ID.")
        return
    confirm = input(f">> Delete order #{oid}? Type DELETE to confirm: ").strip()
    if confirm != "DELETE":
        print("Cancelled.")
        return
    ok = delete_order(oid)
    if ok:
        print("Order deleted.")

def view_orders_menu() -> None:
    orders = _list_orders_basic()
    if not orders:
        return
    detail = input(">> View line-items for a specific order? Enter ID or press Enter: ").strip()
    if detail == "":
        return
    try:
        oid = int(detail)
    except ValueError:
        print("Please enter a numeric ID.")
        return
    for o in orders:
        if int(o.get("order_id", -1)) == oid:
            print(f"\nOrder #{oid} details:")
            for li in o.get("items", []):
                print(f"  - {li.get('name','')} (id={li.get('product_id')}) x{li.get('qty')}  |  Price £{li.get('unit_price',0):.2f}  |  Subtotal £{li.get('subtotal',0):.2f}")
            print(f"Order Total: £{o.get('order_total',0):.2f}")
            return
    print("Order not found.")


def orders_menu() -> None:
    while True:
        print("""\n
+ ===== Orders Menu ===== +
|                         |
| 1. Create Orders        |
| 2. Edit Orders          |
| 3. Delete Orders        |
| 4. View Orders          |
| 5. Sort Orders          |
| 6. Main Menu.           |
|                         |
+ ----------------------- +\n
""")
        orders_choice = input("Select 1-6: \n").strip()
        if orders_choice == "1":
            create_order_menu()
        elif orders_choice == "2":
            edit_order_menu()
        elif orders_choice == "3":
            delete_order_menu()
        elif orders_choice == "4":
            view_orders_menu()
        elif orders_choice == "5":
            break
        else:
            print("* Invalid selection. Please enter a number between 1 and 5.")
