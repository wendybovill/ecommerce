class Product:
  """
  A model for the products to be created.
  The product can select a Category and a season and is
  linked to those models through their Primary Keys.
  The products do not have to select a Category or a
  season, but it does make searching for the product
  in the store easier. An image can be uploaded or added
  by a url. The product Name is a required field as is
  the tag.
  """
  def __init__(self, product_data):
    self.product_data = product_data if product_data is not None else {}
    self.next = None

  def __str__(self):
    return self.Name

  class Meta:
    verbose_Name_plural = 'products'
    
class Node(Product):
  def __init__(self, data):
    self.data = data
    self.next = None

def traverseAndPrint(head):
  currentNode = head
  while currentNode:
    print(currentNode.data, end="\n")
    currentNode = currentNode.next
  print(indexNode)

def writeToFile(data):
    with open("products.txt", "a") as file:
        file.write(str(data))

def insertNodeAtPosition(head, newNode, position):
  if position == 1:
    newNode.next = head
    return newNode

  currentNode = head
  for _ in range(position - 2):
    if currentNode is None:
      break
    currentNode = currentNode.next

  newNode.next = currentNode.next
  currentNode.next = newNode
  return head


def DictToString():
    DictToString = {
        "Name" : input("Enter Product Name: "),
        "Category" : input("Enter Product Category: "),
        "Price" : float(input("Enter Product Price: £ ")),
        "stock" : int(input("Enter Stock Qty: "))
        }
    return str(DictToString)

def getData():
    # ProductData = DictToString()
    # return ProductData
    # ProductData = "\n" + "Product Name: " + input("Enter Product Name: ") + "\n" + "Category: " + input(
    #     "Enter Product Category: ") + "\n" + "Price: £ " + input(
    #         "Enter Product Price: £") +"\n" + "Stock Qty: " + input(
    #         "Enter Stock Qty: ") + "\n" + "Number of Orders: " + input(
    #             "Enter Number of Orders: ") + "\n____________\n"
    try:
        with open("products.txt", "r") as file:
            content = file.readlines()
            if content:
                print("Existing Products:")
                for line in content:
                  print(*line.strip("{").strip(" }").split(", "), sep="\n")
            else:
                print("No products added yet.")
    except FileNotFoundError:
      print("The file does not exist.")
      return content

def addData():
    # ProductData = DictToString()
    # return ProductData
    NewData = {"Product Name: " + input("Enter Product Name: "),
               "Category: " + input("Enter Product Category: "),
               "Price: £ " + input("Enter Product Price: £"),
               "Stock Qty: " + input("Enter Stock Qty: "),
               }
    return str(NewData)

def addProduct():
  product_data = {
    "Name" : str(input("Enter your Product Name: ")),
    "Category" : str(input("Product Category: ")),
    "Price" : float(input("Price: £ ")),
    "Stock" : int(input("Stock Qty: ")),
    "Orders" : "",
  }
  return str(product_data)

def indexNode(head, index):
  currentNode = head
  count = 0
  while currentNode:
    if count == index:
      return currentNode
    count += 1
    currentNode = currentNode.next
  return None

def readDataFromFile():
    try:
        with open("products.txt", "r") as file:
            content = file.readlines()
            print("Products in file:")
            for line in content:
              print(*line.split(", "), sep="\n")
    except FileNotFoundError:
        print("The file does not exist.")
node1 = Node(getData())
indexNode(node1, 0)


# Insert a new product with value 97 at position 2
newNode = Node(addProduct())
node1 = insertNodeAtPosition(node1, newNode, 2)
# print("Original list:")
traverseAndPrint(node1)
writeToFile(newNode.data)
readDataFromFile()
