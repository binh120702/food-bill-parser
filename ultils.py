from openai import OpenAI
import json
from datetime import datetime
from good_list import Goods, GoodsList

def get_client(api_key):
    """
    Returns an OpenAI client instance.
        
    Returns:
        OpenAI: An instance of the OpenAI client.
    """
    return OpenAI(api_key=api_key)

def extract_food_bills(bill_text: str,  client=None):
    """
    Extracts food bills into three columns: name of goods, quantity, and price using OpenAI API.
    
    Parameters:
        bill_text (str): The text of the receipt.
        api_key (str): OpenAI API key.
        
    Returns:
        return a good list with the extracted data.
        GoodList: A list of Good objects with the extracted data.
    """

    tools = [{
        'type': 'function',
        'name': 'extract_food_bills',
        'description': 'Extracts food bills into three columns: name of goods, quantity, and price',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Name of the goods'
                },
                'quantity': {
                    'type': 'number',
                    'description': 'Quantity of the goods'
                },
                'price': {
                    'type': 'number',
                    'description': 'Price of the goods, notice that the dot is not a decimal point, it is a separator'
                }
            },
            'required': ['name', 'quantity', 'price']
        }
    },{
        'type': 'function',
        'name': 'extract_food_bills_timestamp',
        'description': 'Extracts food bills timestamp into 4 columns: month, day, hour, minute',
        'parameters': {
            'type': 'object',
            'properties': {
                'month': {
                    'type': 'integer',
                    'description': 'Month of the timestamp'
                },
                'day': {
                    'type': 'integer',
                    'description': 'Day of the timestamp'
                },
                'hour': {
                    'type': 'integer',
                    'description': 'Hour of the timestamp'
                },
                'minute': {
                    'type': 'integer',
                    'description': 'Minute of the timestamp'
                },
                
            },
            'required': ['month', 'day', 'hour', 'minute']
        }
    }]
    
    try : 
        response = client.responses.create(
            model="gpt-4o",
            input=[{"role": "user", "content": bill_text}],
            tools=tools
        )
        goods_list = GoodsList()
        timestamp = None
        for objects in response.output:
            args = json.loads(objects.arguments)
            if objects.name == 'extract_food_bills_timestamp':
                current_time = datetime.now()
                month = args['month']
                day = args['day']
                hour = args['hour']
                minute = args['minute']
                if month > current_time.month:
                    year = current_time.year - 1
                else:
                    year = current_time.year
                timestamp = datetime(year, month, day, hour, minute).strftime("%Y-%m-%d %H:%M:%S")
                
        for objects in response.output:
            args = json.loads(objects.arguments)
            if objects.name == 'extract_food_bills':
                
                goods_list.add_goods(Goods(
                    name=args['name'],
                    quantity=args['quantity'],
                    price=args['price'],
                    person_in_charge="shared",
                    datetime=timestamp
                ))
    
        return goods_list
    except Exception as e:
        print(f"Error processing response: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    bill_text = """
    1. Apple 2 pcs $3.00
    2. Banana 1 pcs $1.50
    3. Orange 3 pcs $4.50
    """
    
    client = get_client()
    stocks = extract_food_bills(bill_text, client)
    print(stocks)