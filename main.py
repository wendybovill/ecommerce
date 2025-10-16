import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import menus.menus as main_menu


BASE_DIR = Path(__file__).resolve().parent.parent   # -> project root
DATA_DIR = BASE_DIR / "storage"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_PRODUCT_PATH = DATA_DIR / "product_catalog.json"
DEFAULT_CATEGORIES_PATH = DATA_DIR / "category_catalog.json"

if __name__ == "__main__":

    main_menu()
