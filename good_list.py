
from dataclasses import dataclass

@dataclass
class Goods:
    name: str = ""
    quantity: float = 0.0
    price: float = 0.0
    person_in_charge: str = "shared"
    datetime: str = ""
    
    def __init__(self, name, quantity, price, person_in_charge="shared", datetime=""):
        self.name = name
        self.quantity = quantity
        self.price = price
        self.person_in_charge = person_in_charge
        self.datetime = datetime

class GoodsList:
    def __init__(self):
        self.goods = []
    
    def add_goods(self, good: Goods):
        self.goods.append(good)
        
    def add_a_goods_list(self, goods: 'GoodsList'):
        """Add a list of goods to the GoodsList""" 
        for good in goods.goods:
            self.add_goods(good)