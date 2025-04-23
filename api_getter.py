import requests
from good_list import GoodsList, Goods
from datetime import datetime
import json

json_data = {
    "pageIndex": 1,
    "pageSize": 0
}

def preprocess_data(data):
    # Preprocess the data as needed
    # For example, you might want to extract specific fields or format the data
    # return data
    processed_data = GoodsList()
    for bill in data['data']:
        for item in bill['listSaleOrderOnline'][0]['listProduct']:
            processed_item = Goods(
                datetime = bill['listSaleOrderOnline'][0].get('deliveryTime'),
                quantity= item.get('quantity'),
                price= item.get('salePrice'),
                name= item.get('productName'),
                image_url= item.get('avatar'),
            )
            processed_item.price = processed_item.price * processed_item.quantity
            # processed_item.datetime = datetime.fromisoformat(processed_item.datetime).strftime("%B %d, %Y at %I:%M %p (%Z%z)")
            processed_data.add_goods(processed_item)
    return processed_data

def get_api_data(headers, valid_date):
    # Make the API request
    print("Sending request to API...")
    headers = json.loads(headers)
    response = requests.post('https://apibhx.tgdd.vn/History/GetListingHistory', headers=headers, json=json_data)
    print("Received response from API.")
    print(f"Response status code: {response.status_code}")
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        return preprocess_data(data).get_goods_valid_date(valid_date)
    # If the request was not successful, handle the error
    else:
        print(f"Error: {response.status_code}")
        return None