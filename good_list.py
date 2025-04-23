
from dataclasses import dataclass
import datetime
@dataclass
class Goods:
    name: str = ""
    quantity: float = 0.0
    price: float = 0.0
    person_in_charge: str = "shared"
    datetime: str = ""
    image_url: str = ""
    
    def __init__(self, name, quantity, price, person_in_charge="shared", datetime="", image_url=""):
        self.name = name
        self.quantity = quantity
        self.price = price
        self.person_in_charge = person_in_charge
        self.datetime = datetime
        self.image_url = image_url

class GoodsList:
    def __init__(self):
        self.goods = []
    
    def add_goods(self, good: Goods):
        self.goods.append(good)
        
    def add_a_goods_list(self, goods: 'GoodsList'):
        """Add a list of goods to the GoodsList""" 
        for good in goods.goods:
            self.add_goods(good)
    
    def get_goods_valid_date(self, start_date: datetime.datetime):
        """Get goods that are valid from a certain date"""
        valid_goods_list = GoodsList()
        for good in self.goods:
            if datetime.datetime.fromisoformat(good.datetime).replace(tzinfo=None) >= start_date :
                valid_goods_list.add_goods(good)
        return valid_goods_list
    
    def to_dict(self):
        """Convert the GoodsList to a dictionary"""
        return [good.__dict__ for good in self.goods]