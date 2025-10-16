import os
from typing import List, Dict, Tuple, Optional, Iterable, Set
from pathlib import Path
import json
from functions.product_manager import load_products, save_products
from env import DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH, DEFAULT_CUSTOMER_PATH
   
# Resolve storage
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "storage"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_CATEGORIES_PATH = DATA_DIR / "category_catalog.json"

# Classes
class Category:
    """A product category, possibly with a parent (for hierarchy)."""
    def __init__(self, category_id: int, name: str, parent_id: Optional[int] = None):
        self.category_id = int(category_id)
        self.name = str(name)
        self.parent_id = int(parent_id) if parent_id is not None else None

    # Serialize for JSON
    def to_dict(self) -> Dict:
        return {"category_id": self.category_id, "name": self.name, "parent_id": self.parent_id}

    # Construct from dict with legacy keys tolerated
    def from_dict(d: Dict) -> "Category":
        cid = d.get("category_id", d.get("id"))
        return Category(
            category_id=int(cid),
            name=str(d.get("name", "")).strip(),
            parent_id=(int(d["parent_id"]) if d.get("parent_id") not in (None, "", "null") else None),
        )
    class Meta:
        verbose_name_plural = 'categories'

    def sub_category(self, name, tag, description):
        self.name = name
        self.tag = tag
        self.description = description
        
        class Meta:
            verbose_name_plural = 'sub_categories'
        return self.tag
    

# Import products helpers for propagation / checks

def _load_categories(path: Path = DEFAULT_CATEGORIES_PATH) -> Tuple[List[Category], bool]:
    """
    Returns (categories, wrapped). If file missing/invalid: ([], False).
    Supports legacy shapes:
      - {"categories":[{...}]}
      - [{...}]
    """
    if not path.exists():
        return [], False
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return [], False

    wrapped = False
    raw_list: Iterable[Dict] = []
    if isinstance(data, dict) and isinstance(data.get("categories"), list):
        wrapped = True
        raw_list = data["categories"]
    elif isinstance(data, list):
        raw_list = data
    else:
        return [], False

    out: List[Category] = []
    for d in raw_list:
        # Back-compat: if legacy lacked parent_id, treat as top-level
        if "parent_id" not in d:
            d = {**d, "parent_id": None}
        try:
            out.append(Category.from_dict(d))
        except Exception:
            continue
    return out, wrapped

def _save_categories(categories: List[Category], wrapped: bool, path: Path = DEFAULT_CATEGORIES_PATH) -> None:
    payload = {"categories": [c.to_dict() for c in categories]} if wrapped else [c.to_dict() for c in categories]
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

# =============== Helpers ===============

def _next_category_id(categories: List[Category]) -> int:
    max_id = 0
    for c in categories:
        try:
            max_id = max(max_id, int(c.category_id))
        except (TypeError, ValueError):
            continue
    return max_id + 1 if max_id >= 0 else 1

def _index(categories: List[Category]) -> Dict[int, Category]:
    return {int(c.category_id): c for c in categories}

def _children_of(categories: List[Category], parent_id: Optional[int]) -> List[Category]:
    return [c for c in categories if c.parent_id == parent_id]

def _descendant_ids(categories: List[Category], root_id: int) -> Set[int]:
    """All descendant category_ids (children, grandchildren, …)."""
    ids: Set[int] = set()
    pending = [root_id]
    by_parent: Dict[Optional[int], List[Category]] = {}
    for c in categories:
        by_parent.setdefault(c.parent_id, []).append(c)
    while pending:
        pid = pending.pop()
        kids = by_parent.get(pid, [])
        for k in kids:
            if k.category_id not in ids:
                ids.add(k.category_id)
                pending.append(k.category_id)
    return ids

def _name_exists(categories: List[Category], name: str, parent_id: Optional[int]) -> bool:
    """Case-insensitive name uniqueness per same parent."""
    norm = name.strip().casefold()
    for c in categories:
        if c.parent_id == parent_id and c.name.strip().casefold() == norm:
            return True
    return False

# =============== Public API (flat + tree) ===============

def list_categories(path: Path = DEFAULT_CATEGORIES_PATH) -> List[Dict]:
    """
    Flat list (for back-compat): each dict has category_id, name, parent_id.
    Sorted: parents first (name), then their subcategories (name).
    """
    categories, _ = _load_categories(path)
    result: List[Category] = []
    parents = sorted(_children_of(categories, None), key=lambda c: c.name.casefold())
    for p in parents:
        result.append(p)
        children = sorted(_children_of(categories, p.category_id), key=lambda c: c.name.casefold())
        result.extend(children)
    return [c.to_dict() for c in result]

def list_category_tree(path: Path = DEFAULT_CATEGORIES_PATH) -> List[Dict]:
    """
    Hierarchical structure for display:
    [ { node: {id,name,parent_id}, children: [ ... ] }, ... ]
    """
    categories, _ = _load_categories(path)
    by_parent: Dict[Optional[int], List[Category]] = {}
    for c in categories:
        by_parent.setdefault(c.parent_id, []).append(c)
    for v in by_parent.values():
        v.sort(key=lambda c: c.name.casefold())

    def build(parent_id: Optional[int]) -> List[Dict]:
        nodes = []
        for c in by_parent.get(parent_id, []):
            nodes.append({"node": c.to_dict(), "children": build(c.category_id)})
        return nodes

    return build(None)

def add_category(name: str, path: Path = DEFAULT_CATEGORIES_PATH) -> Optional[Dict]:
    """Add a top-level (parent) category."""
    return add_subcategory(name=name, parent_id=None, path=path)

def add_subcategory(name: str, parent_id: Optional[int], path: Path = DEFAULT_CATEGORIES_PATH) -> Optional[Dict]:
    """Add a category under parent_id (None => top-level). Enforces sibling-name uniqueness."""
    if not isinstance(name, str) or not name.strip():
        print("Category name is required.")
        return None

    categories, wrapped = _load_categories(path)
    if parent_id is not None:
        index = _index(categories)
        if int(parent_id) not in index:
            print("Parent category not found.")
            return None

    if _name_exists(categories, name, parent_id):
        print("Category already exists under this parent.")
        return None

    new_cat = Category(category_id=_next_category_id(categories), name=name.strip(), parent_id=parent_id)
    categories.append(new_cat)
    _save_categories(categories, wrapped, path)
    level = "Parent" if parent_id is None else f"Sub-category of {parent_id}"
    print(f"Added {level}: '{new_cat.name}' (id={new_cat.category_id})")
    return new_cat.to_dict()

def update_category_name(
    category_id: int,
    new_name: str,
    *,
    path: Path = DEFAULT_CATEGORIES_PATH,
    products_path: Path = DEFAULT_PRODUCT_PATH
) -> bool:
    """Rename a category (unique among siblings). Propagate new name to products referencing this category_id."""
    if not new_name or not new_name.strip():
        print("New name cannot be empty.")
        return False

    categories, wrapped = _load_categories(path)
    index = _index(categories)
    target = index.get(int(category_id))
    if not target:
        print("Category ID not found.")
        return False

    if _name_exists(categories, new_name, target.parent_id):
        print("A category with that name already exists under the same parent.")
        return False

    old = target.name
    target.name = new_name.strip()
    _save_categories(categories, wrapped, path)

    # Propagate to products (only this exact category_id)
    products = load_products(products_path)
    changed = False
    for product in products:
        try:
            if int(product.get("category_id", -1)) == int(category_id):
                product["category_name"] = target.name
                changed = True
        except (TypeError, ValueError):
            continue
    if changed:
        save_products(products, products_path)

    print(f"Renamed category id={category_id} from '{old}' to '{target.name}'")
    return True

def delete_category(
    category_id: int,
    *,
    path: Path = DEFAULT_CATEGORIES_PATH,
    products_path: Path = DEFAULT_PRODUCT_PATH
) -> bool:
    """
    Delete a category ONLY if:
      - It has no sub-categories (direct children)
      - No products reference it
    (We do NOT delete subtrees automatically to avoid surprises.)
    """
    categories, wrapped = _load_categories(path)
    index = _index(categories)
    target = index.get(int(category_id))
    if not target:
        print("Category ID not found.")
        return False

    # Block if there are children
    has_children = any(c.parent_id == int(category_id) for c in categories)
    if has_children:
        print("Cannot delete: category has sub-categories. Delete or move them first.")
        return False

    # Block if products reference this category
    products = load_products(products_path)
    blockers = []
    for products in products:
        try:
            if int(products.get("category_id", -1)) == int(category_id):
                blockers.append(products)
        except (TypeError, ValueError):
            continue

    if blockers:
        for products in blockers:
            print(f"Assigned to product ({products.get('name','(unnamed)')} and ID {products.get('product_id','unknown')}). "
                  "Please change product category before deleting this category")
        return False

    # Perform delete
    kept = [c for c in categories if int(c.category_id) != int(category_id)]
    _save_categories(kept, wrapped, path)
    print(f"Deleted category id={category_id} ('{target.name}')")
    return True

def delete_all_categories(
    *,
    path: Path = DEFAULT_CATEGORIES_PATH,
    products_path: Path = DEFAULT_PRODUCT_PATH
) -> bool:
    """
    Delete ALL categories only if no products currently have a category assigned.
    (Hierarchy doesn’t matter here.)
    """
    categories, wrapped = _load_categories(path)
    if not categories:
        _save_categories([], wrapped, path)
        print("All categories deleted.")
        return True

    products = load_products(products_path)
    blockers = [products for products in products if products.get("category_id") not in (None, "", 0)]
    if blockers:
        for products in blockers:
            print(f"Assigned to product ({products.get('name','(unnamed)')} and ID {products.get('product_id','unknown')}). "
                  "Please change product category before deleting this category")
        print("Delete ALL cancelled due to assigned categories.")
        return False

    _save_categories([], wrapped, path)
    print("All categories deleted.")
    return True

def _build_parent_index(categories: List[Category]) -> Dict[Optional[int], List[Category]]:
    by_parent: Dict[Optional[int], List[Category]] = {}
    for c in categories:
        by_parent.setdefault(c.parent_id, []).append(c)
    # sort siblings by name for stable numbering
    for v in by_parent.values():
        v.sort(key=lambda x: x.name.casefold())
    return by_parent

def compute_category_display_codes(
    path: Path = DEFAULT_CATEGORIES_PATH,
    start_at: int = 10
) -> Dict[int, str]:
    """
    Return a map {category_id: 'code'} like:
      ParentA -> '10',   ChildA1 -> '10.1', ChildA2 -> '10.2'
      ParentB -> '11',   ChildB1 -> '11.1'
    Codes are computed by (name-sorted) sibling order.
    """
    categories, _ = _load_categories(path)
    by_parent = _build_parent_index(categories)
    id_to_code: Dict[int, str] = {}

    # depth-first numbering
    def assign_codes(parent_id: Optional[int], prefix: Optional[str], next_num_start: int) -> None:
        siblings = by_parent.get(parent_id, [])
        if prefix is None:
            # top-level: 10, 11, 12, ...
            num = next_num_start
            for c in siblings:
                code = f"{num}"
                id_to_code[c.category_id] = code
                # children: 10.1, 10.2...
                assign_codes(c.category_id, code, 1)
                num += 1
        else:
            # children: prefix.1, prefix.2, ...
            index = 1
            for c in siblings:
                code = f"{prefix}.{index}"
                id_to_code[c.category_id] = code
                assign_codes(c.category_id, code, 1)
                index += 1

    assign_codes(None, None, start_at)
    return id_to_code

def get_category_id_by_display_code(
    code: str,
    path: Path = DEFAULT_CATEGORIES_PATH,
    start_at: int = 10
) -> Optional[int]:
    """
    Resolve a dotted display code like '10' or '10.2' to an integer category_id.
    """
    mapping = compute_category_display_codes(path=path, start_at=start_at)
    # invert the mapping
    for cid, ccode in mapping.items():
        if ccode == code.strip():
            return cid
    return None

def list_subcategories_by_parent_code(
    parent_code: str,
    *,
    path: Path = DEFAULT_CATEGORIES_PATH,
    start_at: int = 10,
    include_all_descendants: bool = False
) -> List[Dict]:
    """
    Return sub-categories belonging to the parent identified by a display code (e.g., '10' or '10.2').
    - include_all_descendants=False: direct children only
    - include_all_descendants=True: all levels (children, grandchildren, ...)
    Each result is a dict: {category_id, name, parent_id}
    """
    parent_id = get_category_id_by_display_code(parent_code, path=path, start_at=start_at)
    if parent_id is None:
        print("Parent code not found.")
        return []

    categories, _ = _load_categories(path)

    if not include_all_descendants:
        # Direct children only
        children = sorted(
            _children_of(categories, parent_id),
            key=lambda c: c.name.casefold()
        )
        return [c.to_dict() for c in children]

    # All descendants (any depth)
    desc_ids = _descendant_ids(categories, int(parent_id))
    results = [c.to_dict() for c in categories if int(c.category_id) in desc_ids]
    # Sort nicely by (level via name path). Simple name sort is OK for now:
    results.sort(key=lambda d: str(d.get("name", "")).casefold())
    return results

def list_subcategories_with_codes_by_parent_code(
    parent_code: str,
    *,
    path: Path = DEFAULT_CATEGORIES_PATH,
    start_at: int = 10,
    include_all_descendants: bool = False
) -> List[Dict]:
    """
    Same as list_subcategories_by_parent_code, but includes a 'display_code' in each result.
    Returns: [{category_id, name, parent_id, display_code}, ...]
    """
    id_to_code = compute_category_display_codes(path=path, start_at=start_at)
    items = list_subcategories_by_parent_code(
        parent_code,
        path=path,
        start_at=start_at,
        include_all_descendants=include_all_descendants
    )
    for it in items:
        it["display_code"] = id_to_code.get(int(it["category_id"]), "")
    # Sort by code for a tidy hierarchical feel
    items.sort(key=lambda d: d.get("display_code",""))
    return items

def _code_for_id(category_id: int, categories_path: Path, code_start: int) -> str:
    codes = compute_category_display_codes(categories_path, start_at=code_start)
    return codes.get(int(category_id), "")
