import os
import json
from pathlib import Path
from env import DATA_DIR, DEFAULT_CUSTOMER_PATH, DEFAULT_ORDER_PATH, DEFAULT_PRODUCT_PATH, DEFAULT_CATEGORIES_PATH, DEFAULT_REPORTS_PATH
from menus.menu_category import category_menu
from menus.menu_product import product_menu
from menus.menu_orders import orders_menu

PRODUCTS_PATH: Path = DEFAULT_PRODUCT_PATH        # data_files/product_catalog.json
CATEGORIES_PATH: Path = DEFAULT_CATEGORIES_PATH    # data_files/category_catalog.json
ORDERS_PATH: Path = DEFAULT_ORDER_PATH              # data_files/orders.json
CUSTOMERS_PATH: Path = DATA_DIR / "customers.json"  # data_files/customers.json

#========= Main Menu Section =========
# Defining the Main Menu and adding Menu Functions

def main_menu():
    """
    This is the function to display the Main Menu
    and to call relevant menu's display functions
    """
    print("""\n
+ ===== Main Menu ====== +
|                        |
| 1. Products            |
| 2. Categories          |
| 3. Customer            |
| 4. Orders              |
| 5. All Records         |
| 6. Exit Ecommerce App  |
|                        |
+ ---------------------- +\n
""")

    main_menu_choice = input(">> Please select option (1-6): ")

    if main_menu_choice == "1":
        product_menu()
    elif main_menu_choice == "2":
        category_menu()
    elif main_menu_choice == "3":
        customer_menu()
    elif main_menu_choice == "4":
        orders_menu()
    elif main_menu_choice == "5":
        view_all_records()
    elif main_menu_choice == "6":
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Exiting Ecommerce App.")
        exit(0)
    else:
        print("* Invalid selection. Please enter a number between 1 and 6.")


#========= Customer Section =========
# Add a new Customer
def add_customer():
    """
    This is the function to add a new customer
    """
    customer = {
        "fname" : input("Enter Customer First Name: "),
        "lname" : input("Enter Customer Last Name: "),
        "email" : input("Enter Customer Email Address: "),
        "address" : {
            "line_1" : input("Enter Address Line 1: "),
            "line_2" : input("Enter Address Line 2: "),
            "town_or_city" : input("Enter Town/City: "),
            "county" : input("Enter County: "),
            "post_code" : input("Enter Post Code: "),
            "country" : input("Enter Country"),
        }
    }
    print("\nIs Delivery Address the same as Address?\n")
    delivery_choice = input("Select:\n1 For Yes\n2 To Enter Delivery Address")

    if delivery_choice == "1":
        with open(CUSTOMERS_PATH, "a") as file:
            # file.write(customer + "\n")
            json.dumps(customer + "\n")
        with open(DEFAULT_REPORTS_PATH, "w") as file:
            file.write("customer")
            # json.dumps(customer + "\n")
        print("Customer added successfully!")
        print("Returning to Customer Menu.")
        customer_menu()
    elif delivery_choice == "2":
        print("Enter Delivery Address")
        def add_customer_delivery_address():
            customer.delivery_address = {
                "line_1" : input("Enter Address Line 1: "),
                "line_2" : input("Enter Address Line 2: "),
                "town_or_city" : input("Enter Town/City: "),
                "county" : input("Enter County: "),
                "post_code" : input("Enter Post Code: "),
                "country" : input("Enter Country"),
                }
        add_customer_delivery_address()
        with open(DEFAULT_CUSTOMER_PATH, "a+") as file:
            json.dumps(customer + "\n")
        with open(records_file, "a") as file:
            # file.write(customer + "\n")
            json.dumps(customer + "\n")
        print("Customer added successfully!")
        print("Returning to Customer Menu.")
        customer_menu()
    else:
        print("Invalid choice. Please enter a number between 1 and 2.")


# View Customers
def view_customers():
    """
    This is the function to view all customers
    """
    try:
        with open(DEFAULT_CUSTOMER_PATH, "r") as file:
            customers = file.read()
            if customers:
                print("\n--- Viewing Customers ---")
                print(customers)
            else:
                print("\nNo customers found.")
    except FileNotFoundError:
        print("No customers found.")


# Delete all customers
def delete_all_customers():
    """
    This is the function to view all customers
    """
    confirm = input("Are you sure you want to delete all customers? (Yes/No): ")
    if confirm.lower() == "yes":
        with open(customers_file, "w") as file:
            pass
        print("All customers have been deleted")
    else:
        print("Deletion cancelled")
        print("Returning to Customer Menu.")
        customer_menu()


# ==== MAIN CUSTOMER MENU 
def customer_menu():
    """
    This is the function to display the Product Menu
    and to call relevant CUSTOMER functions
    """
    print("""\n    
+ ==== Customer Menu ==== +
|                         |
| 1. Add a new Customer   |
| 2. View all Customers   |
| 3. Edit Customer        |
| 4. Delete a Customer    |
| 5. Delete all Customers |
| 6. Return to Main Menu  |
|                         |
+ ----------------------- +\n
""")

    customer_choice = input(">> Please select option (1-6): ")

    if customer_choice == "1":
        add_customer()
    elif customer_choice == "2":
        view_customers()
    elif customer_choice == "3":
        edit_customer()
    elif customer_choice == "4":
        delete_customer()
    elif customer_choice == "5":
        delete_all_customers()
    elif customer_choice == "6":
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Returning to Main Menu.")
        main_menu()
    else:
        print("Invalid selection. Please enter a number between 1 and 6.")


# #========= Products Section =========

# # Define Product Class

# class Product:
#     """
#     A model for the products to be created.
#     The product can select a category and a season and is
#     linked to those models through their Primary Keys.
#     The products do not have to select a category or a
#     season, but it does make searching for the product
#     in the store easier. An image can be uploaded or added
#     by a url. The product name is a required field as is
#     the tag.
#     """

#     def __init__(self, name, category, price, stock):
#         id = pid()
#         self.name = str(name.input("Enter your Product Name: "))
#         self.category = str(category.input("Product Category: "))
#         self.price = str(price(float).input("Price: £ "))
#         self.stock = str(stock(int).input("Stock Qty: "))

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name_plural = 'products'

# # Add a new product
# def get_pid():
#     try:
#         if os.path.exists(products_file):
#             with open(products_file, "r") as file:
#                 products_content = json.load(file)
#                 if products_content:
#                     last_product = products_content[-1]
#                     current_pid = last_product['id'] + 1
#                     pid = current_pid + 1
#                 else:
#                     pid = 1
#                     return pid
#         else:
#             return 1
#     except:
#         print("Error getting Product ID")

# def add_product():
#     """
#     This is the function to add a new product
#     """
#     id = get_pid()
#     name = input("Enter your Product Name: ")
#     category = input("Product Category: ")
#     price = input("Price: £ ")
#     stock = input("Stock Qty: ")
#     newline = "\n"

#     with open(products_file, "r", encoding="utf-8-sig") as file:
#         products_content = json.load(file)
#         if products_content:
#             new_product = {
#             "id": id,
#             "name": input("Enter name: "),
#             "category": input("Enter category: "),
#             "price": int(input("Enter price: ")),
#             "stock": int(input("Enter stock: ")),
#             }
#             new_data = products_content.append(new_product)
#             with open(products_file, "w", encoding="utf-8-sig") as file:
#                 json.dump(new_data, file, indent=4)
#         else:
#             with open(products_file, "a", encoding="utf-8-sig") as file:
#             #print("Error Accessing File")
#             # product_str = json.dumps(Product, indent=4)
#                 file.write(new_product)
#             # print(Product)
#             print("Product Error - Please try again.")
#             product_menu()

# # View all products
# def view_products():
#     """
#     This is the function to view all products
#     """

#     try:
#         with open(products_file, "r") as file:
#             product_content = file.read()
#             # product_str = json.loads(product_content)
            
#             if product_content:
#                 def display_product_info():
#                     """
#                     Displays the products's information.
#                     """
#                     # Convert JSON string to a Python object
                    
#                     # Iterate through the JSON array
#                     print("\n--- Your products ---")
#                     print(product_content)
#                     for x in file.readlines():
#                         print(x, end='')
#                     # for item in product_data:
#                     #     print(f"Name: {item['name']}")
#             else:
#                 print("\nNo products found.")
#                 product_menu()
#     except FileNotFoundError:
#         print("No products found.")
#         product_menu()

# # Delete all products
# def delete_products():
#     """
#     This is the function to DELETE all products
#     """
#     confirm = input("Are you sure you want to delete all products? (Yes/No): ")
#     if confirm.lower() == "yes":
#         with open(products_file, "w") as file:
#             pass
#         print("All products have been deleted")
#     else:
#         print("Deletion cancelled")
#         print("Returning to Product Menu.")
#         product_menu()

# # ==== MAIN PRODUCT MENU 
# def product_menu():
#     """
#     This is the function to display the Product Menu
#     and to call relevant PRODUCT functions
#     """
#     print("\n--- Product Menu---\n")
#     print("Please select: ")
#     print("1. Add a new Product")
#     print("2. View all Products")
#     print("3. Edit Product")
#     print("4. Delete a Product")
#     print("5. Delete all Product")
#     print("6. Return to Main Menu")

#     product_menu_choice = input("Enter your choice (1-6): ")

#     if product_menu_choice == "1":
#         add_product()
#     elif product_menu_choice == "2":
#         view_products()
#     elif product_menu_choice == "3":
#         edit_product()
#     elif product_menu_choice == "4":
#         delete_product()
#     elif product_menu_choice == "5":
#         delete_products()
#     elif product_menu_choice == "6":
#         os.system('cls' if os.name == 'nt' else 'clear')
#         print("Returning to Main Menu.")
#         main_menu()
#     else:
#         print("Invalid choice. Please enter a number between 1 and 6.")

# View all records in one file
def view_all_records():
    try:
        with open(records_file, "r", encoding="utf-8") as file:
            content = json.loads(file)
            json_str = json.dumps(content)
            if content:
                while True:
                    print("\n--- Viewing All Records ---")
                    print(json_str)
                    choice = input("Select:\n1 to Return to Main Menu\n2 to Exit Ecommerce App")
                    if choice == "1":
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Returning to Main Menu.")
                        main_menu()
                    elif choice == "2":
                        os.system('cls' if os.name == 'nt' else 'clear')
                        exit(1)
                    else:
                        print("Invalid choice. Please enter a number between 1 and 2.")
            else:
                print("\nNo records found.")
    except FileNotFoundError:
        print("No records found.")


# Main Program Loop
while True:
    main_menu()