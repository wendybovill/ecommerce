
import json

class Category:
    """
    A model for categories to be created for the products.
    The product can select a category so is linked to the
    category primary key. The categories are independent
    of the products, and seasons. Categories can have images.
    """
    def __init__(self, name, friendly_name, tag, description, discount, image, image_url):
        self.name = name
        self.friendly_name = friendly_name
        self.tag = tag
        self.description = description
        self.discount = discount
        self.image = image
        self.image_url = image_url
   
    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name

    def image_preview(self):
        return mark_safe(f'<img src = "{self.image.url}" width = "150"/>')

    class Meta:
        verbose_name_plural = 'categories'


class Season:
    """
    A model for seasons to be created for the products.
    The product can select a season so is linked to the
    season primary key. The seasons are independent
    of the products, and categories.
    """
    def __init__(self, name, friendly_name):
        self.name = name
        self.friendly_name = friendly_name
   
    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name

    class Meta:
        verbose_name_plural = 'seasons'


class Product(Category, Season):
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
    
    def __init__(self, name, sku, category, description, size, tag, price, image, image_url, colours, discount, specialoffer, multipleproducts, stock, season, friendly_name,has_sizes):
        
        self.name = name
        self.sku = sku
        self.category = category.name
        self.description = description
        self.size = size(str)
        self.tag = tag(str)
        self.price = price(float)
        self.image = image
        self.image_url = image_url(str)
        self.colours = colours(str)
        self.discount = discount(float)
        self.specialoffer = specialoffer(bool)
        self.multipleproducts = multipleproducts(str)
        self.stock = stock(int)
        self.season = self.season.season
        self.friendly_name = friendly_name
        self.has_sizes = has_sizes

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name

    def image_preview(self):
        return (f'<img src = "{self.image.url}" width = "150"/>')

    class Meta:
        verbose_name_plural = 'products'    

    def display_product_info(self, product):
        """
        Displays the products's information.
        """
        print(f"Product: {self.name}\nPrice: {self.price}\nDetails:"),
        print(f" Description: {self.description}"),
        print(f" Size: {self.size}")
        print(f" Colours: {self.colours}")
        print(f" Category: {self.category.name}")
        print(f" Special Offer?: {self.specialoffer}")
        print(f" Stock: {self.stock}")
        if Season is not None:
            print(f" Season: {self.season.season}")
        else:
            return