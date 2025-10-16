# functions/order_store.py
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime
import uuid
from decimal import Decimal
from env import DEFAULT_ORDER_PATH, DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH, DEFAULT_CUSTOMER_PATH
from functions.product_manager import delete_product, load_products, save_products, add_product, _convert_product_price_from_string, _convert_product_stock, _sorted_product, sort_products, _convert_product_price_from_string
from functions.category_manager import list_categories, add_category
from functions.product_categories import get_category_menu, assign_category_to_product_by_index
from functions.customer_manager import list_customers_sorted, get_customer_by_id, get_customer_orders

ORDERS_PATH: Path = DEFAULT_ORDER_PATH
PRODUCT_PATH: Path = DEFAULT_PRODUCT_PATH
CUSTOMER_PATH: Path = DEFAULT_CUSTOMER_PATH
CATEGORY_PATH: Path = DEFAULT_CATEGORIES_PATH


# ---------------- Load ----------------

def load_orders(path: Path = DEFAULT_ORDER_PATH) -> List[Dict]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def save_orders(orders: List[Dict], path: Path = DEFAULT_ORDER_PATH) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def _next_order_id(orders: List[Dict]) -> int:
    max_id = 0
    for o in orders:
        try:
            max_id = max(max_id, int(o.get("order_id", 0)))
        except (TypeError, ValueError):
            continue
    return max_id + 1 if max_id >= 0 else 1

# ---------------- Utilities ----------------

def _normalize_items(items: List[Dict]) -> Optional[List[Dict]]:
    """
    Ensure items: [{"product_id": int, "qty": int}, ...] with qty >= 1
    """
    if not isinstance(items, list) or not items:
        return None
    norm: List[Dict] = []
    for it in items:
        try:
            pid = int(it.get("product_id"))
            qty = int(it.get("qty"))
        except (TypeError, ValueError):
            return None
        if pid <= 0 or qty <= 0:
            return None
        norm.append({"product_id": pid, "qty": qty})
    return norm

def _index_products_by_id(products: List[Dict]) -> Dict[int, Dict]:
    index = {}
    for s in products:
        try:
            index[int(s.get("product_id"))] = s
        except (TypeError, ValueError):
            continue
    return index

def _calc_lines_and_total(norm: List[Dict], product_by_id: Dict[int, Dict]) -> Tuple[List[Dict], float]:
    grand_total = 0.0
    line_items: List[Dict] = []
    for it in norm:
        p = product_by_id[it["product_id"]]
        price = float(p.get("price", 0.0) or 0.0)
        line_total = round(price * it["qty"], 2)
        grand_total = round(grand_total + line_total, 2)
        line_items.append({
            "product_id": it["product_id"],
            "name": p.get("name", ""),
            "qty": it["qty"],
            "price": price,
            "subtotal": line_total,       # labelled "Subtotal"
        })
    return line_items, grand_total

# ---------------- Public API ----------------

def add_order(
    items: List[Dict],
    *,
    customer_id: int,
    orders_path: Path = DEFAULT_ORDER_PATH,
    products_path: Path = DEFAULT_PRODUCT_PATH,
    allow_negative_stock: bool = False
) -> Optional[Dict]:
    """
    Create an order: items=[{product_id:int, qty:int}, ...], customer_id required.
    Applies stock decrement and total_ordered increment.
    """
    norm = _normalize_items(items)
    if norm is None:
        print("Invalid items. Expect a non-empty list of {product_id, qty>=1}.")
        return None

    try:
        cid = int(customer_id)
        if cid <= 0:
            raise ValueError
    except (TypeError, ValueError):
        print("Invalid customer_id.")
        return None

    products = load_products(products_path)
    if not products:
        print("No products exist.")
        return None
    product_by_id = _index_products_by_id(products)

    # Validate existence + stock
    for it in norm:
        pid = it["product_id"]
        qty = it["qty"]
        product = product_by_id.get(pid)
        if not product:
            print(f"Product with product_id {pid} not found.")
            return None
        cur_stock = int(product.get("product_stock", 0) or 0)
        if not allow_negative_stock and cur_stock - qty < 0:
            name = product.get("name", "(unnamed)")
            print(f"Insufficient stock for '{name}' (id {pid}). Have {cur_stock}, need {qty}.")
            return None

    # Build order object
    orders = load_orders(orders_path)
    order_id = _next_order_id(orders)
    order_uuid = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"

    line_items, grand_total = _calc_lines_and_total(norm, product_by_id)

    order = {
        "order_id": order_id,
        "order_uuid": order_uuid,
        "customer_id": cid,
        "created_at": created_at,
        "items": line_items,          # each has price and subtotal
        "order_total": grand_total,   # grand total
    }
    orders.append(order)
    save_orders(orders, orders_path)

    # Update product totals & stock
    for it in norm:
        p = product_by_id[it["product_id"]]
        p["product_total_ordered"] = int(p.get("product_total_ordered", 0) or 0) + it["qty"]
        p["product_stock"] = int(p.get("product_stock", 0) or 0) - it["qty"]
    save_products(products, products_path)

    print(f"Created order #{order_id} (uuid {order_uuid}) for customer #{cid} | total £{grand_total:.2f}")
    return order

def edit_order(
    order_id: int,
    new_items: List[Dict],
    *,
    orders_path: Path = DEFAULT_ORDER_PATH,
    products_path: Path = DEFAULT_PRODUCT_PATH,
    allow_negative_stock: bool = False
) -> Optional[Dict]:
    """
    Replace an order's items with new_items (same format as add_order).
    Safely restocks previous items, then applies new stock deductions.
    """
    orders = load_orders(orders_path)
    target = None
    for o in orders:
        try:
            if int(o.get("order_id")) == int(order_id):
                target = o
                break
        except (TypeError, ValueError):
            continue
    if not target:
        print("Order not found.")
        return None

    norm = _normalize_items(new_items)
    if norm is None:
        print("Invalid items. Expect a non-empty list of {product_id, qty>=1}.")
        return None

    products = load_products(products_path)
    product_by_id = _index_products_by_id(products)

    # Step 1: Restock old items / roll back totals
    for li in target.get("items", []):
        pid = int(li.get("product_id"))
        qty = int(li.get("qty", 0))
        p = product_by_id.get(pid)
        if p:
            p["product_total_ordered"] = int(p.get("product_total_ordered", 0) or 0) - qty
            p["product_stock"] = int(p.get("product_stock", 0) or 0) + qty

    # Step 2: Validate new stock availability
    for it in norm:
        pid, qty = it["product_id"], it["qty"]
        p = product_by_id.get(pid)
        if not p:
            print(f"Product with product_id {pid} not found.")
            # restore original state
            for li in target.get("items", []):
                ps = product_by_id.get(int(li.get("product_id")))
                if ps:
                    ps["product_total_ordered"] = int(ps.get("product_total_ordered", 0) or 0) + int(li.get("qty", 0))
                    ps["product_stock"] = int(ps.get("product_stock", 0) or 0) - int(li.get("qty", 0))
            save_products(products, products_path)
            return None
        cur_stock = int(p.get("product_stock", 0) or 0)
        if not allow_negative_stock and cur_stock - qty < 0:
            print(f"Insufficient stock for '{p.get('name','(unnamed)')}' (id {pid}). Have {cur_stock}, need {qty}.")
            # restore original state
            for li in target.get("items", []):
                ps = product_by_id.get(int(li.get("product_id")))
                if ps:
                    ps["product_total_ordered"] = int(ps.get("product_total_ordered", 0) or 0) + int(li.get("qty", 0))
                    ps["product_stock"] = int(ps.get("product_stock", 0) or 0) - int(li.get("qty", 0))
            save_products(products, products_path)
            return None

    # Step 3: Apply new items to stock + totals
    for it in norm:
        p = product_by_id[it["product_id"]]
        p["product_total_ordered"] = int(p.get("product_total_ordered", 0) or 0) + it["qty"]
        p["product_stock"] = int(p.get("product_stock", 0) or 0) - it["qty"]
    save_products(products, products_path)

    # Step 4: Recompute order lines + total
    line_items, grand_total = _calc_lines_and_total(norm, product_by_id)
    target["items"] = line_items
    target["order_total"] = grand_total
    save_orders(orders, orders_path)
    print(f"Edited order #{order_id} | new total £{grand_total:.2f}")
    return target

def delete_order(
    order_id: int,
    *,
    orders_path: Path = DEFAULT_ORDER_PATH,
    products_path: Path = DEFAULT_PRODUCT_PATH
) -> bool:
    """
    Delete an order and restock products / roll back totals.
    """
    orders = load_orders(orders_path)
    index = -1
    for i, o in enumerate(orders):
        try:
            if int(o.get("order_id")) == int(order_id):
                index = i
                break
        except (TypeError, ValueError):
            continue
    if index == -1:
        print("Order not found.")
        return False

    # Restock + roll back totals
    products = load_products(products_path)
    product_by_id = _index_products_by_id(products)
    for li in orders[index].get("items", []):
        pid = int(li.get("product_id"))
        qty = int(li.get("qty", 0))
        p = product_by_id.get(pid)
        if p:
            p["product_total_ordered"] = int(p.get("product_total_ordered", 0) or 0) - qty
            p["product_stock"] = int(p.get("product_stock", 0) or 0) + qty
    save_products(products, products_path)

    removed = orders.pop(index)
    save_orders(orders, orders_path)
    print(f"Deleted order #{removed.get('order_id')} (uuid {removed.get('order_uuid')}).")
    return True

# --------- helpers to list / filter ---------

def list_orders(*, orders_path: Path = DEFAULT_ORDER_PATH) -> List[Dict]:
    """All orders, most recent first."""
    data = load_orders(orders_path)
    def _key(o):
        return (o.get("created_at", ""), int(o.get("order_id", 0)))
    return sorted(data, key=_key, reverse=True)

def list_orders_for_customer(customer_id: int, *, orders_path: Path = DEFAULT_ORDER_PATH) -> List[Dict]:
    out = [o for o in load_orders(orders_path) if int(o.get("customer_id", -1)) == int(customer_id)]
    def _key(o):
        return (o.get("created_at", ""), int(o.get("order_id", 0)))
    return sorted(out, key=_key, reverse=True)

def get_orders_for_product(product_id: int, *, orders_path: Path = DEFAULT_ORDER_PATH) -> List[Dict]:
    out: List[Dict] = []
    for o in load_orders(orders_path):
        for li in o.get("items", []):
            try:
                if int(li.get("product_id")) == int(product_id):
                    out.append({
                        "order_id": o.get("order_id"),
                        "order_uuid": o.get("order_uuid"),
                        "qty": li.get("qty"),
                        "price": li.get("price"),
                        "subtotal": li.get("subtotal"),
                        "created_at": o.get("created_at"),
                    })
            except (TypeError, ValueError):
                continue
    def _key(r):
        return (r.get("created_at", ""), int(r.get("order_id", 0)))
    return sorted(out, key=_key, reverse=True)
