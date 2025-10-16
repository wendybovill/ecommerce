from typing import Dict, Optional, List
from pathlib import Path
from functions.category_manager import list_categories, add_category
from functions.product_manager import load_products, save_products
from env import DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH

def get_category_menu(categories_path: Path = DEFAULT_CATEGORIES_PATH, allow_add: bool = True) -> List[str]:
    """
    Returns display lines (strings) Menu.
    """
    categories = list_categories(categories_path)
    lines = [f"{i+1}. {category['name']} (id={category.get('category_id', category.get('id'))})" for i, category in enumerate(categories)]
    if allow_add:
        lines.append(f"{len(categories)+1}. + Add a new category…")
    return lines

def apply_category_choice_to_product(
    product: Dict,
    selection_index: int,
    *,
    categories_path: Path = DEFAULT_CATEGORIES_PATH,
    new_category_name: Optional[str] = None,
    allow_add: bool = True
) -> Optional[Dict]:
    """
    Mutates `product` to set 'category_id' and 'category_name' by selection index (1-based).
    Returns chosen/created category dict, or None if invalid/failed.
    """
    categories = list_categories(categories_path)
    max_index = len(categories) + (1 if allow_add else 0)
    if selection_index < 1 or selection_index > max_index:
        print("Invalid selection index.")
        return None

    if selection_index <= len(categories):
        chosen = categories[selection_index - 1]
    else:
        if not new_category_name or not new_category_name.strip():
            print("new_category_name is required to add a new category.")
            return None
        added = add_category(new_category_name.strip(), path=categories_path)
        if not added:
            return None
        chosen = added

    product["category_id"] = int(chosen.get("category_id", chosen.get("id")))
    product["category_name"] = chosen["name"]
    return chosen

def assign_category_to_product_by_index(
    products_index: int,
    category_selection_index: int,
    *,
    products_path: Path = DEFAULT_PRODUCT_PATH,
    categories_path: Path = DEFAULT_CATEGORIES_PATH,
    new_category_name: Optional[str] = None,
    allow_add: bool = True
) -> bool:
    """
    High-level: choose a product by zero-based index, apply category selection,
    and save back to disk.
    """
    products = load_products(products_path)
    if not products or products_index < 0 or products_index >= len(products):
        print("Invalid product index.")
        return False

    product = products[products_index]
    chosen = apply_category_choice_to_product(
        product,
        category_selection_index,
        categories_path=categories_path,
        new_category_name=new_category_name,
        allow_add=allow_add,
    )
    if not chosen:
        return False

    save_products(products, products_path)
    print(f"Assigned '{product.get('name','(unnamed)')}' → {chosen['name']} (id={chosen.get('category_id', chosen.get('id'))})")
    return True
