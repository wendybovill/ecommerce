
import json
from sympy import content


class Products:
    def __init__(self, Name, Category, Price, Stock, Orders):
        self.Name = Name
        self.Category = Category
        self.Price = Price
        self.Stock = Stock
        self.Orders = Orders
    
def view_products(Products):
    # for Product in Products:
    #     print(f"Product: {Product.Name}, Category: {Product.Category}, Price: £{Product.Price}, Stock: {Product.Stock}, Orders: {Product.Orders}")
    print(str(Products))

def view_product(self):
    print(f"Product: {self.Name}, Category: {self.Category}, Price: £{self.Price}, Stock: {self.Stock}, Orders: {self.Orders}")

def update_stock(self, new_stock):
    self.Stock = new_stock
    print(f"Updated stock for {self.Name}: {self.Stock}")

def readDataFromFile():
    try:
        with open("products.txt", "r") as file:
            ProductList = json.loads(file)
            print("Products in file:")
            print(ProductList)
            # for Product in Products:
            #   print(*Product.split(", "), sep="\n")
    except FileNotFoundError:
        print("The file does not exist.")

def view_products(ProductList):
    # for Product in Products:
    print(ProductList)


def view_product(ProductList, Product):
    Product = next((p for p in ProductList if p['Name'] == Product.Name), None)
    if Product:
        print(f"Product: {Product['Name']}, Category: {Product['Category']}, Price: £{Product['Price']}, Stock: {Product['Stock']}, Orders: {Product['Orders']}")


# Products = [{"Name": "Laptop", "Category": "Electronics", "Price": 999.99, "Stock": 10, "Orders": 5},
#                 {"Name": "Smartphone", "Category": "Electronics", "Price": 699.99, "Stock": 15, "Orders": 8},
#                 {"Name": "Headphones", "Category": "Accessories", "Price": 199.99, "Stock": 25, "Orders": 12}
#                 ]

view_products(Products)