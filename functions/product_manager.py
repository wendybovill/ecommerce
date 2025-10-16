from pathlib import Path
import json
import os
from typing import List, Dict, Optional
from env import BASE_DIR, DATA_DIR, DEFAULT_ORDER_PATH, DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH
from decimal import Decimal



def load_products(path: Path = DEFAULT_PRODUCT_PATH) -> List[Dict]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def save_products(products: List[Dict], path: Path = DEFAULT_PRODUCT_PATH) -> None:
    """Save formatted product to JSON file."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def _next_product_id(products: List[Dict]) -> int:
    """Calculate product_id for a new product."""
    max_id = 0
    for product in products:
        try:
            max_id = max(max_id, int(product.get("product_id", 0)))
        except (TypeError, ValueError):
            continue
    return max_id + 1 if max_id >= 0 else 1


def _convert_product_price_from_string(price_str: str) -> Decimal | None:
    """ Converting price from input
    Validating: '12', '12.50', '£12.50', '12,50'.
    """
    if price_str is None:
        return None
    product = str(price_str).strip().replace(",", "")
    # strip currency symbols
    for symbol in ("£", "$", "€"):
        if product.startswith(symbol):
            product = product[len(symbol):].strip()
            break
    try:
        val = float(product)
        if val < 0:
            return None
        return round(val, 2)
    except ValueError:
        return None

def _convert_product_stock(stock_str: str) -> Optional[int]:
    """ Converting stock from input.
    Validating: '0', '12', '0012'. Must be a positive integer.
    """
    if stock_str is None:
        return None
    product = str(stock_str).strip()
    if not product.isdigit():
        return None
    return int(product)

def add_product(
    name: str,
    price: str,
    stock: str,
    path: Path = DEFAULT_PRODUCT_PATH
) -> Optional[Dict]:
    """
    Adds a new product with next product_id, price, and description.
    - name: required non-empty string
    - price: parsed to a non-negative float (2dp). If invalid, prints an error and returns None.
    - product_description: optional; stored as provided (trimmed)
    """
    if not isinstance(name, str) or not name.strip():
        print("Product name is required.")
        return None
    name = name.strip()

    price_val = _convert_product_price_from_string(price)
    
    if price_val is None:
        print("Product price is invalid. Please enter a non-negative number (e.g., 12.50).")
        return None

    stock_val = _convert_product_stock(stock)
    
    if stock_val is None:
        print("Product stock is invalid. Please enter a non-negative whole number (e.g., 0 or 25).")
        return None

    products = load_products(path)
    new_id = _next_product_id(products)

    product = {
        "product_id": new_id,
        "name": name.strip(),
        "price": price_val,                       # numeric
        "stock": stock_val,                        # int
        "category_id": None,
        "category_name": None,
    }
    products.append(product)
    save_products(products, path)
    print(f"Added product '{product['name']}' with product_id {product['product_id']}), "
          f"(price {product['price']:.2f})")

    print(
        f"Product Added: '{product['name']}' (ID: {product['product_id']}), "
        f"                Price: {product['price']:.2f}, Stock: {product['stock']}"
    )
    return product


def delete_product(
    product_id: int,
    *,
    products_path: Path = DEFAULT_PRODUCT_PATH,
    orders_path: Path = DEFAULT_ORDER_PATH
) -> bool:
    """
    Delete a product (product) by ID. If any order references this product,
    cancel deletion and print blocking order IDs.
    """
    products = load_products(products_path)
    if not products:
        print("No products to delete.")
        return False

    # Check orders for references
    blockers = []
    if orders_path.exists():
        try:
            with orders_path.open("r", encoding="utf-8") as f:
                orders = json.load(f)
            if isinstance(orders, list):
                for order in orders:
                    oid = order.get("order_id")
                    for li in order.get("items", []):
                        try:
                            if int(li.get("product_id")) == int(product_id):
                                blockers.append(oid)
                        except (TypeError, ValueError):
                            continue
        except (json.JSONDecodeError, OSError):
            pass

    if blockers:
        uniq = sorted(set(b for b in blockers if b is not None))
        print(f"Cannot delete: product is referenced by orders {uniq}.")
        return False

    kept: List[Dict] = []
    removed = None
    for product in products:
        try:
            if int(product.get("product_id", -1)) == int(product_id):
                removed = product
            else:
                kept.append(product)
        except (TypeError, ValueError):
            kept.append(product)

    if not removed:
        print("Product ID not found.")
        return False

    save_products(kept, products_path)
    print(f"Deleted product '{removed.get('name','(unnamed)')}' (id {product_id}).")
    return True


def _sorted_product(by: str, direction: str, *, products_path: Path = DEFAULT_PRODUCT_PATH) -> List[Dict]:
    products = load_products(products_path)
    reverse = str(direction).lower() == "desc"

    def safe_int(v) -> int:
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0

    def safe_float(v) -> float:
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    def key(p: Dict):
        if by == "id":
            return safe_int(p.get("product_id") or p.get("id"))
        if by == "name":
            return str(p.get("name", "")).casefold()
        if by == "price":
            return safe_float(p.get("price"))
        if by == "orders":
            return safe_int(p.get("order_tally") or p.get("total_ordered") or p.get("orders"))
        if by == "stock":
            return safe_int(p.get("stock"))
        return safe_int(p.get("product_id") or p.get("id"))

    return sorted(products, key=key, reverse=reverse)

def sort_products(
    *,
    by: str = "id",
    direction: str = "asc",
    products_path: Path = DEFAULT_PRODUCT_PATH
) -> List[Dict]:
    return _sorted_product(by=by, direction=direction, products_path=products_path)


def calculate_product_order_tally(
    *,
    products_path: Path = DEFAULT_PRODUCT_PATH,
    orders_path: Path = DEFAULT_ORDER_PATH
) -> None:
    """
    Recompute each product's 'order_tally' by summing across orders.
    Does not adjust stock — this is for consistency checking or backfilling.
    """
    products = load_products(products_path)
    if not products:
        print("No products to update.")
        return

    # Index products
    index = {}
    for i, p in enumerate(products):
        try:
            index[int(p.get("product_id"))] = i
        except (TypeError, ValueError):
            continue

    # Sum quantities per product
    totals = {pid: 0 for pid in index.keys()}
    if orders_path.exists():
        try:
            with orders_path.open("r", encoding="utf-8") as f:
                orders = json.load(f)
            if isinstance(orders, list):
                for o in orders:
                    for li in o.get("items", []):
                        try:
                            pid = int(li.get("product_id"))
                            qty = int(li.get("qty", 0))
                            if pid in totals:
                                totals[pid] += max(0, qty)
                        except (TypeError, ValueError):
                            continue
        except (json.JSONDecodeError, OSError):
            pass

    # Write back totals
    changed = False
    for pid, total in totals.items():
        i = index[pid]
        if int(products[i].get("order_tally", 0) or 0) != int(total):
            products[i]["order_tally"] = int(total)
            changed = True

    if changed:
        save_products(products, products_path)
        print("Updated Ordered Products Tally")
    else:
        print("Totals already up to date.")
        
def _fmt_product_line(i: int, product: Dict) -> str:
    name = product.get("name", "(unnamed)")
    category = product.get("category_name") or "-"
    price = product.get("price")
    stock = product.get("stock")
    total_ord = product.get("order_tally", 0) or 0

    price_str = f" | £{price:.2f}" if isinstance(price, (int, float)) else ""
    stock_str = f" | stock: {stock}" if isinstance(stock, int) else ""
    orders_str = f" | ordered: {int(total_ord)}"
    return f"  {i}. {name} (id={product.get('product_id')}) | category: {category}{price_str}{stock_str}{orders_str}"

