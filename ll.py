'''
A simple linked list implementation in Python.
'''


class Product():
    """
    A model for the products to be created.
    The product can select a category and a season and is
    linked to those models through their Primary Keys.
    The products do not have to select a category or a
    season, but it does make searching for the product
    in the store easier. An image can be uploaded or added
    by a url. The product name is a required field as is
    the tag.
    """

    def __init__(self, name, category, price, stock):
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'products'
        
def add_product():
    """
    This is the function to add a new product
    """
    Product = {
        "name" : input("Enter your Product Name: "),
        "category" : input("Product Category: "),
        "price" : input("Price: £ "),
        "stock_qty" : input("Stock Qty: ")
        }
        
class Node():
  def __init__(self, data):
    self.data = add_product()
    self.next = None

    def __str__(self):
        return self.data
    

def traverseAndPrint(head):
  currentNode = head
  while currentNode:
    print(currentNode.data, end=" -> ")
    currentNode = currentNode.next
  print("null")

node1 = Node()
node2 = Node(11)
node3 = Node(3)
node4 = Node(2)
node5 = Node(9)

node1.next = node2
node2.next = node3
node3.next = node4
node4.next = node5

traverseAndPrint(node1)

products_file = "products.txt"
try:
    with open(products_file, "r") as file:
        product_content = file.readlines()
    if product_content:
        with open(products_file, "a") as file:
            # file.write(str(Product))
            product_str = json.dumps(str(Product), indent=4)
            # product_str = json.dumps(Product, indent=4) --- IGNORE ---
            # file.write(Product + "\n") --- IGNORE ---
            print(Product)
            print("New Product added successfully!")

    else:
        with open(products_file, "w") as file:
            #print("Error Accessing File")
            product_str = json.dumps(Product, indent=4)
            file.write(Product)
            print(Product)
            print("Product added successfully!")

except FileNotFoundError:
    with open(products_file, "w") as file:
        #print("Error Accessing File")
        product_str = json.dumps(Product, indent=4)
        file.write(Product)
        print(Product)
        print("Product added successfully!")
except Exception as e:
    print(f"An error occurred: {e}")