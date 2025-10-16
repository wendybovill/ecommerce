# functions/customer_store.py
from typing import List, Dict, Optional
from pathlib import Path
import json
import re
from datetime import datetime
from env import BASE_DIR, DEFAULT_CATEGORIES_PATH, DEFAULT_CUSTOMER_PATH, DEFAULT_ORDER_PATH, DEFAULT_PRODUCT_PATH
from decimal import Decimal


# ---------------- Basic load/save ----------------

def load_customers(path: Path = DEFAULT_CUSTOMER_PATH) -> List[Dict]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def save_customers(customers: List[Dict], path: Path = DEFAULT_CUSTOMER_PATH) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

def _next_customer_id(customers: List[Dict]) -> int:
    max_id = 0
    for c in customers:
        try:
            max_id = max(max_id, int(c.get("customer_id", 0)))
        except (TypeError, ValueError):
            continue
    return max_id + 1 if max_id >= 0 else 1

# ---------------- Validation helpers ----------------

_EMAIL_RE = re.compile(r"^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$", re.IGNORECASE)

def validate_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email or ""))

def _luhn_check(num: str) -> bool:
    s = "".join(ch for ch in str(num) if ch.isdigit())
    if not s:
        return False
    total, alt = 0, False
    for d in reversed(s):
        n = ord(d) - 48
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return (total % 10) == 0

def _card_brand(num: str) -> str:
    s = "".join(ch for ch in str(num) if ch.isdigit())
    if s.startswith(("34", "37")) and len(s) in (15,):
        return "AMEX"
    if s.startswith(tuple(str(i) for i in range(51, 56))) and len(s) == 16:
        return "Mastercard"
    if s.startswith("4") and len(s) in (13, 16, 19):
        return "Visa"
    if s.startswith(("6011", "65")) and len(s) == 16:
        return "Discover"
    return "Card"

# ---------------- Public API ----------------

def add_customer(
    *,
    title: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    mobile: str,
    home_address: Dict,
    delivery_address: Dict,
    payment_methods: List[Dict],            # each: {type, brand?, last4?, exp_month?, exp_year?}
    preferred_payment_method: str,          # "credit_card" | "debit_card" | "paypal"
    path: Path = DEFAULT_CUSTOMER_PATH
) -> Optional[Dict]:
    """
    Create a customer record. Only stores non-sensitive card info (brand, last4, expiry).
    Returns the created customer dict or None on validation error.
    """
    # Names
    if not first_name.strip() or not last_name.strip():
        print("First and Last names are required.")
        return None

    # Email
    if not validate_email(email):
        print("Invalid email address.")
        return None

    # Normalize & validate payment methods (mask card data!)
    safe_payments: List[Dict] = []
    for pm in (payment_methods or []):
        pm_type = (pm.get("type") or "").strip().lower()
        if pm_type not in ("credit_card", "debit_card", "paypal"):
            print("Payment method type must be one of: credit_card, debit_card, paypal.")
            return None

        if pm_type in ("credit_card", "debit_card"):
            raw = (pm.get("card_number") or "").strip()
            exp_m = str(pm.get("exp_month") or "").strip()
            exp_y = str(pm.get("exp_year") or "").strip()
            holder = (pm.get("card_holder") or "").strip()

            digits = "".join(ch for ch in raw if ch.isdigit())
            if len(digits) < 12 or not _luhn_check(digits):
                print("Invalid card number.")
                return None
            brand = _card_brand(digits)
            if not (exp_m.isdigit() and 1 <= int(exp_m) <= 12 and exp_y.isdigit() and len(exp_y) in (2, 4)):
                print("Invalid card expiry.")
                return None

            safe_payments.append({
                "type": pm_type,
                "brand": brand,
                "last4": digits[-4:],
                "exp_month": int(exp_m),
                "exp_year": int(exp_y) if len(exp_y) == 4 else int("20" + exp_y),
                "card_holder": holder,
            })
        else:
            # PayPal needs an email (we can reuse the customer email if not provided)
            paypal_email = (pm.get("paypal_email") or email).strip()
            if not validate_email(paypal_email):
                print("Invalid PayPal email.")
                return None
            safe_payments.append({
                "type": "paypal",
                "paypal_email": paypal_email
            })

    if preferred_payment_method not in ("credit_card", "debit_card", "paypal"):
        print("Preferred payment method must be credit_card, debit_card, or paypal.")
        return None

    customers = load_customers(path)
    new_id = _next_customer_id(customers)

    customer = {
        "customer_id": new_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "title": title.strip() if title else "",
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
        "mobile": mobile.strip(),
        "home_address": {
            "line1": (home_address.get("line1") or "").strip(),
            "line2": (home_address.get("line2") or "").strip(),
            "line3": (home_address.get("line3") or "").strip(),
            "postcode": (home_address.get("postcode") or "").strip(),
            "country": (home_address.get("country") or "").strip(),
        },
        "delivery_address": {
            "line1": (delivery_address.get("line1") or "").strip(),
            "line2": (delivery_address.get("line2") or "").strip(),
            "line3": (delivery_address.get("line3") or "").strip(),
            "postcode": (delivery_address.get("postcode") or "").strip(),
            "country": (delivery_address.get("country") or "").strip(),
        },
        "payment_methods": safe_payments,                 # non-sensitive only
        "preferred_payment_method": preferred_payment_method,
    }

    customers.append(customer)
    save_customers(customers, path)
    print(f"Added customer '{customer['first_name']} {customer['last_name']}' (id {customer['customer_id']}).")
    return customer

def get_customer_by_id(customer_id: int, path: Path = DEFAULT_CUSTOMER_PATH) -> Optional[Dict]:
    for c in load_customers(path):
        try:
            if int(c.get("customer_id")) == int(customer_id):
                return c
        except (TypeError, ValueError):
            continue
    return None

def list_customers_sorted(path: Path = DEFAULT_CUSTOMER_PATH) -> List[Dict]:
    return sorted(
        load_customers(path),
        key=lambda c: (c.get("last_name","").casefold(), c.get("first_name","").casefold())
    )

def get_customer_orders(
    customer_id: int,
    *,
    orders_path: Path,
) -> List[Dict]:
    """
    Return this customer's orders, most recent first.
    """
    if not orders_path.exists():
        return []
    try:
        with orders_path.open("r", encoding="utf-8") as f:
            orders = json.load(f)
        if not isinstance(orders, list):
            return []
    except (json.JSONDecodeError, OSError):
        return []

    filtered = [o for o in orders if int(o.get("customer_id", -1)) == int(customer_id)]
    # Most recent first by created_at then order_id
    def _key(o):
        return (o.get("created_at", ""), int(o.get("order_id", 0)))
    return sorted(filtered, key=_key, reverse=True)
