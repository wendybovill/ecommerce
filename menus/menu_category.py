from pathlib import Path
from functions.category_manager import add_category, update_category_name, list_categories, delete_category, delete_all_categories, DEFAULT_CATEGORIES_PATH
from env import DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH
from typing import List, Dict, Optional

CATEGORIES_PATH: Path = DEFAULT_CATEGORIES_PATH  # data_files/category_catalog.json
PRODUCTS_PATH: Path = DEFAULT_PRODUCT_PATH    # data_files/product_catalog.json

def category_menu() -> None:
    while True:

        print("""
\n+ === Category Manager === +
|                          |
| 1) List categories       |
| 2) Add category          |
| 3) Edit/Rename category  |
| 4) Delete category       |
| 5) Delete ALL categories |
| 6) Main Menu             |
|                          |
+ ------------------------ +\n
""")
        category_choice = input(">> Please select option (1-6): ").strip()
        if category_choice == "1":
            list_categories_menu()
        elif category_choice == "2":
            add_category_menu()
        elif category_choice == "3":
            edit_category_menu()
        elif category_choice == "4":
            delete_category_menu()
        elif category_choice == "5":
            delete_all_categories_menu()
        elif category_choice == "6":
            return
        else:
            print("* Invalid selection. Please enter a number between 1 and 6.")


def _print_categories() -> None:
    categories = list_categories(CATEGORIES_PATH)
    if not categories:
        print("\nNo categories.")
        return
    print("\nCategories:")
    for category in categories:
        print(f"  - {category['name']} (id={category.get('category_id', category.get('id'))})")

def list_categories_menu() -> None:
    _print_categories()

def add_category_menu() -> None:
    name = input("Enter new category name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    add_category(name, path=CATEGORIES_PATH)

def edit_category_menu() -> None:
    _print_categories()
    raw_id = input("\nEnter the category ID to rename (or Enter to cancel): ").strip()
    if raw_id == "":
        return
    try:
        cid = int(raw_id)
    except ValueError:
        print("Please enter a valid numeric ID.")
        return

    new_name = input("Enter the new category name: ").strip()
    if not new_name:
        print("New name cannot be empty.")
        return
    update_category_name(cid, new_name, path=CATEGORIES_PATH)

def delete_category_menu() -> None:
    _print_categories()
    raw_id = input("\nEnter the category ID to delete (or Enter to cancel): ").strip()
    if raw_id == "":
        return
    try:
        cid = int(raw_id)
    except ValueError:
        print("Please enter a valid numeric ID.")
        return

    confirm = input(f"Delete category id={cid}? Type YES to confirm: ").strip()
    if confirm != "YES":
        print("Cancelled.")
        return
    delete_category(cid, path=CATEGORIES_PATH)
    # NOTE: Product assignments are not auto-updated here.

def delete_all_categories_menu() -> None:
    confirm = input("This will delete ALL categories. Type DELETE to confirm: ").strip()
    if confirm != "DELETE":
        print("Cancelled.")
        return
    delete_all_categories(path=CATEGORIES_PATH)
    # NOTE: Product assignments are not auto-updated here.
