import sqlite3, datetime, requests, json, time, hmac, hashlib

from config import KUNA_API, KUNA_PRIVATE, KUNA_PUBLIC


def save_goods(data):
    connection = sqlite3.connect("database.sqlite")
    cursor = connection.cursor()
    
    insert_statement = "INSERT INTO goods " + \
        "(goods_index, name, region, price, status, images) " + \
        f"VALUES (\"{data['goods_index']}\", \"{data['name']}\", " + \
        f"\"{data['region']}\", {data['price']}, \"available\", " + \
        f"\"{data['images']}\");"
    
    cursor.execute(insert_statement)
    
    connection.commit()
    cursor.close()
    connection.close()

def is_valid_index(index):
    allowed_symbols = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                       'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                       'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                       'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd',
                       'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                       'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                       'y', 'z']
    
    for symbol in index:
        if symbol not in allowed_symbols:
            return False
    
    return True
       
def activate_code(code):
    path = "/v3/auth/kuna_codes/redeem"
    url = KUNA_API + path
    nonce = str(int(time.time()*1000))
    body = ""
    msg = path + nonce + body
    
    kun_signature = hmac.new(KUNA_PRIVATE.encode("ascii"),
                             msg.encode("ascii"),
                             hashlib.sha384).hexdigest()
    
    headers = {
        "Accept": "application/json",
        "kun-nonce": nonce,
        "kun-apikey": KUNA_PUBLIC,
        "kun-signature": kun_signature
    }
    
    params = {"code": code}
    
    responce = requests.put(url, params=params, headers=headers)
    
    if responce.status_code == 200:
        return json.loads(responce.text)
    else:
        return None
    

def get_goods(goods_index=None):
    """Returns data dictionary in next format
    data["name"] = str(),
    data["price"] = int(),
    data["region"] = str(),
    data["creation_date"] = str(),
    data["images"] = str()
    """
    data = list()
    connection = sqlite3.connect("database.sqlite")
    cursor = connection.cursor()
    
    if goods_index:
        select_statement = "SELECT name, price, region, goods_index, images " + \
            "FROM goods WHERE status = \"available\" " + \
            f"AND goods_index = \"{goods_index}\";"
    else:
        select_statement = "SELECT name, price, region, goods_index, images " + \
            "FROM goods WHERE status = \"available\";"
    
    cursor.execute(select_statement)
    for each in cursor.fetchall():
        row = dict()
        row["name"] = each[0]
        row["price"] = each[1]
        row["region"] = each[2]
        row["goods_index"] = each[3]
        row["images"] = each[4]
        data.append(row)
    
    return data

def book_goods(user_id: int, data: dict):
    """Assign goods for user"""
    connection = sqlite3.connect("database.sqlite")
    cursor = connection.cursor()
    
    select_statement = "SELECT goods_id FROM goods " + \
        f"WHERE goods_index = \"{data['goods_index']}\" " + \
        f"AND region = \"{data['region']}\" " + \
        "AND status = \"available\" " + \
        "LIMIT 1;"
    
    cursor.execute(select_statement)
    goods_id = cursor.fetchone()[0]
    
    
    update_statement = "UPDATE goods " + \
        "SET status = \"booked\" " + \
        f"WHERE goods_id = {goods_id};"
        
    cursor.execute(update_statement)
    
    creation_date = datetime.datetime.now().isoformat()
    
    insert_statement = "INSERT INTO orders (user_id, creation_date, " + \
        "status, goods_id) VALUES " + \
        f"({user_id}, \"{creation_date}\", \"opened\", {goods_id});"
        
    cursor.execute(insert_statement)
    
    cursor.close()
    connection.commit()
    connection.close()

def done_goods(user_id: int):
    """In case of end deal"""
    connection = sqlite3.connect("database.sqlite")
    cursor = connection.cursor()
    
    select_statement = "SELECT order_id, goods_id FROM orders " + \
        f"WHERE user_id = {user_id} " + \
        "AND status = \"opened\";"
        
    cursor.execute(select_statement)
    order_id, goods_id = cursor.fetchone()
    
    update_orders = "UPDATE orders " + \
        "SET status = \"done\" " + \
        f"WHERE order_id = {order_id};"
    
    cursor.execute(update_orders)
    
    update_goods = "UPDATE goods " + \
        "SET status = \"done\" " + \
        f"WHERE goods_id = {goods_id};"
    
    cursor.execute(update_goods)
    
    cursor.close()
    connection.commit()
    connection.close()

def unbook_goods(user_id: int):
    """Delete order for specific user"""
    connection = sqlite3.connect("database.sqlite")
    cursor = connection.cursor()
    
    select_statement = "SELECT order_id, goods_id FROM orders " + \
        f"WHERE user_id = {user_id} " + \
        "AND status = \"opened\";"
    
    cursor.execute(select_statement)
    order_id, goods_id = cursor.fetchone()
    
    update_orders = "UPDATE orders " + \
        "SET status = \"rejected\" " + \
        f"WHERE order_id = {order_id};"
    
    cursor.execute(update_orders)
    
    update_goods = "UPDATE goods " + \
        "SET status = \"available\" " + \
        f"WHERE goods_id = {goods_id};"
     
    cursor.execute(update_goods)
    
    cursor.close()
    connection.commit()
    connection.close()

def get_booked_goods(user_id: int):
    """Returns data dictionary in next format
    data["name"] = str(),
    data["price"] = int(),
    data["region"] = str(),
    data["creation_date"] = str(),
    data["images"] = str()
    """
    data = dict()
    connection = sqlite3.connect("database.sqlite")
    cursor = connection.cursor()
    
    select_order = "SELECT goods_id, creation_date FROM orders " + \
        f"WHERE user_id = {user_id} " + \
        "AND status = \"opened\";"
    
    cursor.execute(select_order)
    goods_id, data["creation_date"] = cursor.fetchone()
    
    select_goods = "SELECT name, price, region, images FROM goods " + \
        f"WHERE goods_id = {goods_id};"
    
    cursor.execute(select_goods)
    data["name"], data["price"], data["region"], data["images"] = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return data

def is_user_booked_goods(user_id: int):
    """Check if user is booked order before"""
    connection = sqlite3.connect("database.sqlite")
    cursor = connection.cursor()
    
    select_statement = "SELECT order_id FROM orders " + \
        f"WHERE user_id = {user_id} " + \
        "AND status = \"opened\";"
    
    cursor.execute(select_statement)
    order_id = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return bool(order_id)
