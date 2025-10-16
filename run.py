


product.Name = input("Enter Product Name:")
product.Price = input("Enter Product Price:")
product.Stock = input("Enter Stock Quantity:")
product.SKU = input("Enter Stock Quantity:")
product.pid = ''

class ProductIDCreation:
    def __init__(self, start=1):
        self.counter = start

    def create_product_id(self):
        # Increment the counter and return the ID
        self.counter += 1
        return f"{self.counter}"

# Example usage
pid = ProductIDCreation()
print(pid.create_product_id)