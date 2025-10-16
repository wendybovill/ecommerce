from typing import Dict, Optional, List, Tuple
from pathlib import Path
from functions.category_manager import list_categories, add_category
from functions.product_manager import load_products, save_products
from env import DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH

from functions.product_manager import load_products, save_products, DEFAULT_PRODUCT_PATH
from functions.category_manager import list_categories, add_category, update_category_name, delete_category, delete_all_categories, list_category_tree, compute_category_display_codes, get_category_id_by_display_code, list_subcategories_with_codes_by_parent_code, _code_for_id

PRODUCTS_PATH: Path = DEFAULT_PRODUCT_PATH
CATEGORIES_PATH: Path = DEFAULT_CATEGORIES_PATH


# ---------- Display pickers ----------

def get_category_menu(categories_path: Path = CATEGORIES_PATH, *, allow_add: bool = True) -> List[str]:
    """
    Legacy flat picker (kept for back-compat). Returns numbered lines.
    """
    categories = list_categories(categories_path)
    lines: List[str] = []
    for i, c in enumerate(categories, start=1):
        parent_tag = "" if c.get("parent_id") in (None, "") else "  "
        lines.append(f"{i}. {parent_tag}{c.get('name','')} (id={c.get('category_id')})")
    if allow_add:
        lines.append(f"{len(lines)+1}. + Add a new category…")
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


def get_category_picker_with_codes(categories_path: Path = CATEGORIES_PATH) -> List[str]:
    """
    Hierarchical picker with display codes like:
      - [10] Guitars (id=12)
        - [10.1] Electric (id=13)
    Returns lines (strings) for printing.
    """
    tree = list_category_tree(categories_path)
    codes = compute_category_display_codes(categories_path, start_at=10)

    def _walk(nodes, depth=0) -> List[str]:
        out: List[str] = []
        for n in nodes:
            d = n["node"]
            code = codes.get(int(d["category_id"]), "")
            indent = "  " * depth
            tag = "(Parent)" if d.get("parent_id") in (None, "") else ""
            out.append(f"{indent}- [{code}] {d['name']} (id={d['category_id']}) {tag}".rstrip())
            out.extend(_walk(n["children"], depth + 1))
        return out

    return _walk(tree)


# ---------- Assignment helpers ----------

def assign_category_to_product_by_index(
    *,
    products_index: int,
    category_selection_index: int,
    products_path: Path = PRODUCTS_PATH,
    categories_path: Path = CATEGORIES_PATH,
    new_category_name: Optional[str] = None,
    allow_add: bool = True
) -> bool:
    """
    Existing helper (kept for compatibility with your menu that lists numbered categories).
    """
    products = load_products(products_path)
    if products_index < 0 or products_index >= len(products):
        print("Product index out of range.")
        return False

    categories = list_categories(categories_path)
    if not categories:
        print("No categories exist.")
        return False

    # If "+ Add" was selected, the caller will handle actual creation.
    if allow_add and category_selection_index == len(categories) + 1:
        return False

    try:
        category = categories[category_selection_index - 1]
    except IndexError:
        print("Selection out of range.")
        return False

    cid = int(category.get("category_id"))
    cname = category.get("name", "")

    products[products_index]["category_id"] = cid
    products[products_index]["category_name"] = cname
    save_products(products, products_path)
    print(f"Assigned '{products[products_index].get('name','(unnamed)')}' → {cname} (id={cid})")
    return True


def assign_category_to_product_by_code(
    *,
    products_index: int,
    category_code: str,
    products_path: Path = PRODUCTS_PATH,
    categories_path: Path = CATEGORIES_PATH,
    code_start: int = 10
) -> bool:
    """
    Assign a category to a product by DISPLAY CODE (e.g., '10' or '10.2').
    """
    if not category_code or not str(category_code).strip():
        print("Code is required.")
        return False

    cid = get_category_id_by_display_code(category_code.strip(), path=categories_path, start_at=code_start)
    if cid is None:
        print("Category code not found.")
        return False

    # find the category name for storing on the product
    categories = list_categories(categories_path)
    category = next((c for c in categories if int(c["category_id"]) == int(cid)), None)
    if not category:
        print("Category not found.")
        return False

    products = load_products(products_path)
    if products_index < 0 or products_index >= len(products):
        print("Product index out of range.")
        return False

    products[products_index]["category_id"] = int(cid)
    products[products_index]["category_name"] = category["name"]
    save_products(products, products_path)
    print(f"Assigned '{products[products_index].get('name','(unnamed)')}' → {category['name']} [{category_code}] (id={cid})")
    return True


# ---------- Filtering helpers ----------

def filter_products_by_category_id(
    category_id: int,
    *,
    include_descendants: bool = True,
    products_path: Path = PRODUCTS_PATH,
    categories_path: Path = CATEGORIES_PATH,
    code_start: int = 10
) -> List[Dict]:
    """
    Return all products whose category is category_id (and optionally any descendants of that category).
    """
    products = load_products(products_path)
    if not include_descendants:
        return [product for product in products if int(product.get("category_id", -1)) == int(category_id)]

    # Use category_manager helper that returns all descendants with codes; include the parent too
    # We'll gather descendant IDs and filter products where category_id in that set
    rows = list_subcategories_with_codes_by_parent_code(
        parent_code=_code_for_id(category_id, categories_path, code_start),
        path=categories_path,
        start_at=code_start,
        include_all_descendants=True
    )
    desc_ids = {int(r["category_id"]) for r in rows}
    desc_ids.add(int(category_id))

    return [product for product in products if int(product.get("category_id", -1)) in desc_ids]

def filter_products_by_category_code(
        category_code: str,
        *,
        include_descendants: bool = True,
        products_path: Path = PRODUCTS_PATH,
        categories_path: Path = CATEGORIES_PATH,
        code_start: int = 10
) -> Tuple[List[Dict], Optional[int]]:
    """
    Return (products, parent_id) where 'products' are products under the category represented by category_code.
    If include_descendants=True, includes all nested subcategories.
    """
    cid = get_category_id_by_display_code(category_code.strip(), path=categories_path, start_at=code_start)
    if cid is None:
        print("Category code not found.")
        return [], None

    return filter_products_by_category_id(
        category_id=int(cid),
        include_descendants=include_descendants,
        products_path=products_path,
        categories_path=categories_path,
        code_start=code_start
    ), int(cid)


def _code_for_id(category_id: int, categories_path: Path, code_start: int) -> str:
    codes = compute_category_display_codes(categories_path, start_at=code_start)
    return codes.get(int(category_id), "")
