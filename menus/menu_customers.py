# app_menus/customers_menu.py
from pathlib import Path
from env import DEFAULT_CUSTOMER_PATH, DEFAULT_ORDER_PATH, DEFAULT_CATEGORIES_PATH, DEFAULT_PRODUCT_PATH
from functions.customer_manager import add_customer, list_customers_sorted, get_customer_by_id, get_customer_orders
from functions.order_manager import list_orders
from typing import List, Dict, Optional
from decimal import Decimal


CUSTOMERS_PATH: Path = DEFAULT_CUSTOMER_PATH
ORDERS_PATH: Path = DEFAULT_ORDER_PATH

def _prompt_address(kind: str) -> dict:
    print(f"\nEnter {kind} Address:")
    line1 = input("  Address line 1: ").strip()
    line2 = input("  Address line 2: ").strip()
    line3 = input("  Address line 3: ").strip()
    postcode = input("  Post Code: ").strip()
    country = input("  Country: ").strip()
    return {"line1": line1, "line2": line2, "line3": line3, "postcode": postcode, "country": country}

def _prompt_payment_methods() -> list:
    print("""
Add payment methods (non-sensitive). You can add multiple.
Types:
  1) Credit Card (stores brand, last4, expiry ONLY)
  2) Debit Card  (stores brand, last4, expiry ONLY)
  3) PayPal
Press Enter with no choice to finish.
""")
    methods = []
    while True:
        payment_method_choice = input("Choose type [1/2/3, or Enter to finish]: ").strip()
        if payment_method_choice == "":
            break
        if payment_method_choice not in ("1", "2", "3"):
            print("Invalid choice.")
            continue

        if payment_method_choice in ("1", "2"):
            t = "credit_card" if payment_method_choice == "1" else "debit_card"
            holder = input("  Card holder name: ").strip()
            number = input("  Card number (will NOT be stored, only last4/brand): ").strip()
            exp_m = input("  Expiry month (1-12): ").strip()
            exp_y = input("  Expiry year (YYYY or YY): ").strip()
            methods.append({
                "type": t,
                "card_holder": holder,
                "card_number": number,
                "exp_month": exp_m,
                "exp_year": exp_y,
            })
        else:
            pp = input("  PayPal email (Enter to use customer email): ").strip()
            methods.append({"type": "paypal", "paypal_email": pp})
    return methods

def add_customer_menu() -> None:
    print("\n=== Add Customer ===")
    title = input("Title (optional): ").strip()
    first = input("First name (required): ").strip()
    last = input("Last name (required): ").strip()
    email = input("Email (required): ").strip()
    phone = input("Phone: ").strip()
    mobile = input("Mobile: ").strip()

    home_addr = _prompt_address("Home")
    ship_addr = _prompt_address("Delivery")

    payments = _prompt_payment_methods()

    pref = ""
    while pref not in ("credit_card", "debit_card", "paypal"):
        pref = input("Preferred payment method [credit_card/debit_card/paypal]: ").strip().lower()

    add_customer(
        title=title,
        first_name=first,
        last_name=last,
        email=email,
        phone=phone,
        mobile=mobile,
        home_address=home_addr,
        delivery_address=ship_addr,
        payment_methods=payments,
        preferred_payment_method=pref,
        path=CUSTOMERS_PATH,
    )

def list_customers_menu() -> None:
    customers = list_customers_sorted(CUSTOMERS_PATH)
    if not customers:
        print("\nNo customers.")
        return
    print("\nCustomers:")
    for c in customers:
        cid = c.get("customer_id")
        name = f"{c.get('first_name','')} {c.get('last_name','')}".strip()
        email = c.get("email", "")
        print(f"  - id={cid}: {name} | {email}")

def view_customer_menu() -> None:
    raw = input("\nEnter customer ID to view (or Enter to cancel): ").strip()
    if raw == "":
        return
    try:
        cid = int(raw)
    except ValueError:
        print("Please enter a numeric ID.")
        return

    c = get_customer_by_id(cid, CUSTOMERS_PATH)
    if not c:
        print("Customer not found.")
        return

    # Print core details
    name = f"{c.get('title','')} {c.get('first_name','')} {c.get('last_name','')}".strip()
    print(f"""
=========== Customer #{c.get('customer_id')} ===========
Name: {name}
Email: {c.get('email')}
Phone: {c.get('phone','')}
Mobile: {c.get('mobile','')}
Preferred payment: {c.get('preferred_payment_method')}
""".rstrip())

    ha, da = c.get("home_address", {}), c.get("delivery_address", {})
    print("Home Address:")
    print(f"  {ha.get('line1','')}\n  {ha.get('line2','')}\n  {ha.get('line3','')}\n  {ha.get('postcode','')}\n  {ha.get('country','')}")        
    print("\nDelivery Address:")
    print(f"  {da.get('line1','')}\n  {da.get('line2','')}\n  {da.get('line3','')}\n  {da.get('postcode','')}\n  {da.get('country','')}")

    # Payment methods (masked)
    pms = c.get("payment_methods", [])
    if pms:
        print("\nPayment Methods:")
        for pm in pms:
            t = pm.get("type")
            if t in ("credit_card", "debit_card"):
                print(f"  - {t} {pm.get('brand','Card')} **** **** **** {pm.get('last4','????')}  exp {pm.get('exp_month')}/{pm.get('exp_year')}")
            else:
                print(f"  - PayPal: {pm.get('paypal_email','')}")
    else:
        print("\nPayment Methods: (none)")

    # Orders (most recent first)
    orders = get_customer_orders(cid, orders_path=ORDERS_PATH)
    if not orders:
        print("\nOrders: (none)")
    else:
        print("""\n
              ------------- Customers Orders --------------
              
              Orders (most recent first): \n
              """)
        for o in orders:
            oid = o.get("order_id")
            total = o.get("order_total")
            pro
            created = o.get("created_at")
            print(f"  - Order #{oid}  |  £{total:.2f}  |  {created}")

def customer_menu() -> None:
    while True:
        
        print("""\n
+ ===== Customer Menu ===== +
|                           |
| 1) List Customers         |
| 2) Add Customer           |
| 3) View Customer          |
| 4) Delete Customer        |
| 5) Sort Customers         |
| 6) Main Menu              |
|                           |
+ ------------------------- +\n
""")
        customer_menu_choice = input(">> Please select option (1-6): ").strip()
        if customer_menu_choice == "1":
            list_customers_menu()
        elif customer_menu_choice == "2":
            add_customer_menu()
        elif customer_menu_choice == "3":
            view_customer_menu()
        elif customer_menu_choice == "4":
            delete_customer_menu()
        elif customer_menu_choice == "5":
            sort_customers_menu()
        elif customer_menu_choice == "6":
            break
        else:
            print("Invalid choice.")
