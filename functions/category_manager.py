# functions/category_store.py
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import json
from functions.product_manager import load_products, save_products
from env import DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH
   
# Resolve storage
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "storage"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_CATEGORIES_PATH = DATA_DIR / "category_catalog.json"

# Classes
class Category:
    """
    A model for categories to be created for the products.
    The product can select a category so is linked to the
    category primary key. The categories are independent
    of the products, and seasons. Categories can have images.
    """
    def __init__(self, name, tag, description):
        self.name = name
        self.tag = tag
        self.description = description

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

# Import products helpers for propagation / checks

def _load_categories(path: Path = DEFAULT_CATEGORIES_PATH) -> Tuple[List[Dict], bool]:
    if not path.exists():
        return [], False
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return [], False

    if isinstance(data, dict) and isinstance(data.get("categories"), list):
        return data["categories"], True
    if isinstance(data, list):
        return data, False
    return [], False

def _save_categories(categories: List[Dict], wrapped: bool, path: Path = DEFAULT_CATEGORIES_PATH) -> None:
    payload = {"categories": categories} if wrapped else categories
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def _next_category_id(categories: List[Dict]) -> int:
    max_id = 0
    for category in categories:
        val = category.get("category_id", category.get("id", 0))
        try:
            max_id = max(max_id, int(val))
        except (TypeError, ValueError):
            continue
    return max_id + 1 if max_id >= 0 else 1

def list_categories(path: Path = DEFAULT_CATEGORIES_PATH) -> List[Dict]:
    categories, _ = _load_categories(path)
    return sorted(categories, key=lambda category: str(category.get("name", "")).casefold())

def add_category(name: str, path: Path = DEFAULT_CATEGORIES_PATH) -> Optional[Dict]:
    if not isinstance(name, str) or not name.strip():
        print("Category name is required.")
        return None

    categories, wrapped = _load_categories(path)
    name_orm_new = name.strip().casefold()
    for category in categories:
        if str(category.get("name", "")).strip().casefold() == name_orm_new:
            print("Category already exists")
            return None

    new_id = _next_category_id(categories)
    new_category = {"category_id": new_id, "name": name.strip()}
    categories.append(new_category)
    _save_categories(categories, wrapped, path)
    print(f"Added category '{new_category['name']}' with category_id {new_category['category_id']}")
    return new_category

# ---------- NEW/UPDATED: edit / delete with product propagation & guards ----------

def update_category_name(
    category_id: int,
    update_name: str,
    *,
    path: Path = DEFAULT_CATEGORIES_PATH,
    products_path: Path = DEFAULT_PRODUCT_PATH
) -> bool:
    """
    Rename a category by ID (prevents duplicate names, case-insensitive)
    and propagate the new name to any products that reference this category_id.
    """
    if not update_name or not str(update_name).strip():
        print("New name cannot be empty.")
        return False

    categories, wrapped = _load_categories(path)
    if not categories:
        print("No categories to update.")
        return False

    # Check for duplicate name
    name_orm_new = update_name.strip().casefold()
    if any(str(category.get("name", "")).strip().casefold() == name_orm_new for category in categories):
        print("A category with that name already exists.")
        return False

    # Find and update category
    target = None
    for category in categories:
        cid = category.get("category_id", category.get("id"))
        try:
            if int(cid) == int(category_id):
                target = category
                break
        except (TypeError, ValueError):
            continue

    if target is None:
        print("Category ID not found.")
        return False

    old_name = target.get("name", "")
    target["name"] = update_name.strip()
    _save_categories(categories, wrapped, path)

    # Propagate to products
    products = load_products(products_path)
    changed = False
    for product in products:
        try:
            if int(product.get("category_id", -1)) == int(category_id):
                product["category_name"] = target["name"]
                changed = True
        except (TypeError, ValueError):
            continue
    if changed:
        save_products(products, products_path)

    print(f"Renamed category id={category_id} from '{old_name}' to '{target['name']}'")
    return True

def delete_category(
    category_id: int,
    *,
    path: Path = DEFAULT_CATEGORIES_PATH,
    products_path: Path = DEFAULT_PRODUCT_PATH
) -> bool:
    """
    Delete a single category by ID.
    If any product is assigned to this category, cancel deletion and print:
    'Assigned to product (<title> and ID <product_id>). Please change product category before deleting this category'
    """
    categories, wrapped = _load_categories(path)
    if not categories:
        print("No categories to delete.")
        return False

    # Check products referencing this category
    products = load_products(products_path)
    blockers: List[Dict] = []
    for product in products:
        try:
            if int(product.get("category_id", -1)) == int(category_id):
                blockers.append(product)
        except (TypeError, ValueError):
            continue

    if blockers:
        for product in blockers:
            title = product.get("title", "(untitled)")
            pid = product.get("product_id", "unknown")
            print(f"Assigned to product ({title} and ID {pid}). Please change product category before deleting this category")
        return False

    # Remove the category
    kept: List[Dict] = []
    removed: Optional[Dict] = None
    for category in categories:
        cid = category.get("category_id", category.get("id"))
        try:
            if int(cid) == int(category_id):
                removed = category
            else:
                kept.append(category)
        except (TypeError, ValueError):
            kept.append(category)

    if removed is None:
        print("Category ID not found.")
        return False

    _save_categories(kept, wrapped, path)
    print(f"Deleted category id={category_id} ('{removed.get('name','')})'")
    return True

def delete_all_categories(
    *,
    path: Path = DEFAULT_CATEGORIES_PATH,
    products_path: Path = DEFAULT_PRODUCT_PATH
) -> bool:
    """
    Delete ALL categories. If any product currently has a category assigned,
    cancel and list each blocking product.
    """
    categories, wrapped = _load_categories(path)
    if not categories:
        _save_categories([], wrapped, path)
        print("All categories deleted.")
        return True

    products = load_products(products_path)
    blockers = [product for product in products if product.get("category_id") not in (None, "", 0)]
    if blockers:
        for product in blockers:
            title = product.get("title", "(untitled)")
            pid = product.get("product_id", "unknown")
            print(f"Assigned to product ({title} and ID {pid}). Please change product category before deleting this category")
        print("Delete ALL cancelled due to assigned categories.")
        return False

    _save_categories([], wrapped, path)
    print("All categories deleted.")
    return True
