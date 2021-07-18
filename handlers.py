import json, datetime, os.path, requests

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from config import (
    END, KUNA_API, IMAGES_PATH, ADMIN_IDS, KUNA_INSTRUCTION
    SELECTION_GOODS, SELECTION_REGION, SELECTION_PAYMENT, SUBMIT_PAYMENT,
    REJECT_ORDER, ORDER_MENU, SELECTION_FIELDS, INPUT, CH_INDEX,
    CH_NAME, CH_REGION, CH_PHOTO, CH_PRICE, CH_SUBMIT, CHANGE_FIELD
)

from utils import (
    save_goods,
    is_valid_index,
    activate_code,
    get_goods,
    book_goods,
    done_goods,
    unbook_goods,
    get_booked_goods,
    is_user_booked_goods
)


def cancel(update: Update, context: CallbackContext):
    """Stop adding goods"""
    update.message.reply_text("Adding rejected.")
    
    return END

def stop(update: Update, context: CallbackContext):
    """End conversation by command"""
    update.message.reply_text("Ok, let's start again.\n Enter /start.")
    
    return END

def end(update: Update, context: CallbackContext):
    """End conversation from InlineKeyboardButton"""
    update.callback_query.answer()

    return END

def myorder(update: Update, context: CallbackContext):
    """Check current order"""
    user_id = update.message.from_user.id
    
    if is_user_booked_goods(user_id):
        data = get_booked_goods(user_id)
        text = f"Your order {data['name']}.\n" + \
            f"In region {data['region']}.\n" + \
            f"Created at {data['creation_date']}.\n" + \
            f"Checkout {data['price']}UAH\n" + \
            "Instruction:" + \
            f"{KUNA_INSTRUCTION}"
    
        keyboard = [
            [
                InlineKeyboardButton("Got it.", callback_data=str(END))
            ],
            [
                InlineKeyboardButton("Reject order.",
                                     callback_data=str(REJECT_ORDER))
            ]
        ]
    else:
        text = "You have ordered nothing yet.\n" + \
            "Please use /start to create order."
        
        keyboard = [
            [
                InlineKeyboardButton("Got it.", callback_data=str(END))
            ]
        ]
    
    reply_markup= InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(text=text, reply_markup=reply_markup)
    
    return ORDER_MENU


def start(update: Update, context: CallbackContext):
    """Start command"""
    
    text = "Welcome!\n" + \
           "Python-Telegram-Shop is greeting you!\n" + \
           "There is place where you can buy\n" + \
           "Without leaving your messanger."
    
    keyboard = [
        [
            InlineKeyboardButton("Vinnitsa", callback_data='vn')
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(text=text, reply_markup=reply_markup)

    return SELECTION_GOODS

def select_goods(update: Update, context: CallbackContext):
    """Select available goods"""
    callback_data = update.callback_query.data
    
    if callback_data == "vn":
        city = 'Vinnitsa'
        context.user_data["city"] = "Vinnitsa"
    
    text = f"You have selected {city}.\n Please choose goods."
    
    goods = get_goods()
    indices = set(((i["goods_index"], i["name"]) for i in goods))
    
    buttons = list()
    
    for each in indices:
        buttons.append([InlineKeyboardButton(each[1], callback_data=each[0])])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    
    return SELECTION_REGION

def select_region(update: Update, context: CallbackContext):
    """Select region of city"""
    callback_data = update.callback_query.data
    
    goods = get_goods(goods_index=callback_data)
    
    good = goods[0]
    
    context.user_data["goods"] = good["name"]
    context.user_data["price"] = good["price"]
    context.user_data["goods_index"] = good["goods_index"]
    

    text = f"Chosen: {good['name']}.\n" + \
           f"Price: {good['price']}UAH.\n" + \
           "Please choose region."
    
    regions = set((i["region"] for i in goods))
    
    buttons = list()
    
    for region in regions:
        buttons.append([InlineKeyboardButton(region, callback_data=region)])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    update.callback_query.answer()
    
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    
    return SELECTION_PAYMENT

def select_payment(update: Update, context: CallbackContext):
    """Select payment method"""
    callback_data = update.callback_query.data
    data = dict()
    
    user_id = update.callback_query.from_user.id
    
    data["price"] = context.user_data["price"]
    data["goods"] = context.user_data["goods"]
    data["goods_index"] = context.user_data["goods_index"]
    data["region"] = callback_data
    context.user_data["region"] = callback_data
    
    if not is_user_booked_goods(user_id):
        book_goods(user_id, data)
    else:
        text = "You olready have booked goods.\n" + \
               "To more details /myorder"
        update.callback_query.answer()
        update.callback_query.edit_message_text(text)
        
        return END
    
    text = f"Chosen: {data['goods']}.\n" + \
           f"Price: {data['price']}UAH.\n" + \
           f"Region: {data['region']}."
    
    buttons = [
        [
            InlineKeyboardButton(text=f"Kunacode {data['price']}UAH",
                                 callback_data="kc")
        ],
        [
            InlineKeyboardButton(text="Reject",
                                 callback_data=str(REJECT_ORDER))
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    
    return SUBMIT_PAYMENT

def submit_payment(update: Update, context: CallbackContext):
    """Submit or reject payment"""
    
    text = f"Chosen: {context.user_data['goods']}.\n" + \
        f"Price: {context.user_data['price']}UAH.\n" + \
        f"Region: {context.user_data['region']}.\n" + \
        "In order to use kuna payment please use:\n" + \
        f"{KUNA_INSTRUCTION}"
    
    buttons = [
        [
            InlineKeyboardButton(text="Got it.",
                                 callback_data=str(END))
        ],
        [
            InlineKeyboardButton(text="Reject.",
                                 callback_data=str(REJECT_ORDER))
        ]    
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)    

def waiting_payment(update: Update, context: CallbackContext):
    """Waiting message"""
    
    text = "Ok, we are waiting for payment.\n" + \
        "Check order by using command /myorder."
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return END

def kuna(update: Update, context: CallbackContext):
    """Check and remeed kuna code"""
    user_id = update.message.from_user.id
    
    if not is_user_booked_goods(user_id):
        text = "You have ordered nothing yet.\n" + \
            "To create order please use /start"
        update.message.reply_text(text=text)
        
        return END
    
    if not context.args:
        text = "There is accept kuna code in format\n" + \
            "/kuna 857ny-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-KUN-KCode"
        update.message.reply_text(text=text)
        
        return END
    
    code = context.args[0]
    first_word = code.split('-')[0]
    path = f"/v3/kuna_codes/{first_word}/check"
    responce = requests.get(KUNA_API+path)
    obj = json.loads(responce.text)
    data = get_booked_goods(user_id)
    
    if obj["status"] != "active":
        text = "This code is unactive."
        update.message.reply_text(text=text)
        
        return END
    
    if int(obj["amount"]) < data['price']:
        text = "Value of this code is less then price."
        update.message.reply_text(text)
        
        return END
    
    if activate_code(code):
        images = data["images"].split(',')
        for image in images:
            path = os.path.join(IMAGES_PATH, image)
            file = open(path, 'rb')
            update.message.reply_photo(file)
            file.close()
        
        done_goods(user_id)
        text = "Many thanks!"
        update.message.reply_text(text)
        
        return END

def reject_order(update: Update, context: CallbackContext):
    """Cancel order"""
    
    user_id = update.callback_query.from_user.id
    
    unbook_goods(user_id)
    
    text = "Order has been rejected.\n To start again command /start"
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    
    return END 

def add_goods(update: Update, context: CallbackContext):
    """Starting of add goods proccess"""
    
    user_id = update.message.from_user.id
    
    if user_id not in ADMIN_IDS:
        text = "This for administrator only!"
        update.message.reply_text(text)
        
        return END
    else: 
        text = "Welcome to admin menu."
        
        buttons = [
            [
                InlineKeyboardButton("Create goods",
                                     callback_data="create_goods")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        update.message.reply_text(text=text, reply_markup=keyboard)
        
        return SELECTION_FIELDS

def selection_fields(update: Update, context: CallbackContext):
    """Menu from buttons for select"""
    index = context.user_data.get("added_index", "Nothing")
    name = context.user_data.get("added_name", "Nothing")
    region = context.user_data.get("added_region", "Nothing")
    price = context.user_data.get("added_price", "Nothing")
    photos = context.user_data.get("added_photos", "Nothing")
    
    if index != "Nothing" and not is_valid_index(index):
        text = "Invalid index.\nPlease try again."
        update.message.reply_text(text)
        
        return END
    if price != "Nothing" and not all((ord(i) in range(48, 58) for i in price)):
        text = "Invalid price.\nPlease try again."
        update.message.reply_text(text)
        
        return END
    elif price != "Nothing" and all((ord(i) in range(48, 58) for i in price)):
        price = int(price)
    
    text = "Please select field of goods.\n" + \
        "Current information:\n" + \
        f"Index: {index}\nName: {name}\nRegion: {region}\n" + \
        f"Price:{price}\nPhotos:{photos}\n" + \
        "Cancel addition - /cancel"
    
    buttons = [
        [
            InlineKeyboardButton("Change index.",
                                 callback_data=str(CH_INDEX)),
            InlineKeyboardButton("Change name.",
                                 callback_data=str(CH_NAME))
        ],
        [
            InlineKeyboardButton("Change region.",
                                 callback_data=str(CH_REGION)),
            InlineKeyboardButton("Change price.",
                                 callback_data=str(CH_PRICE))
        ],
        [
            InlineKeyboardButton("Change photos.",
                                 callback_data=str(CH_PHOTO)),
            InlineKeyboardButton("Add into database",
                                 callback_data=str(CH_SUBMIT))
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    if not context.user_data.get("START_OVER"):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text,
                                                reply_markup=keyboard)
    else:
        update.message.reply_text(text=text,
                                  reply_markup=keyboard)
    
    return CHANGE_FIELD

def change_index(update: Update, context: CallbackContext):
    text = "Please type index.\n" + \
        "Buttons of goods will be grouped by this index.\n" + \
        "Index should be short and describle.\n" + \
        "Index should contain latin and digints only.\n" + \
        "For instance: r1g"
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(text)
    
    context.user_data["field"] = "added_index"
    
    return INPUT

def change_name(update: Update, context: CallbackContext):
    text = "Please type name of goods.\n" + \
        "This field will be showing on button."
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(text)
    
    context.user_data["field"] = "added_name"
    
    return INPUT

def change_region(update: Update, context: CallbackContext):
    text = "Please type region.\n" + \
        "Using this field buttons will be group too."

    update.callback_query.answer()
    update.callback_query.edit_message_text(text)
    
    context.user_data["field"] = "added_region"
    
    return INPUT

def change_price(update: Update, context: CallbackContext):
    text = "Please type price.\n" + \
        "Digits valid only."
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(text)
    
    context.user_data["field"] = "added_price"
    
    return INPUT

def change_photo(update: Update, context: CallbackContext):
   text = "Please send photo here.\nAccept jpg format only."
   
   update.callback_query.answer()
   update.callback_query.edit_message_text(text)
   
   context.user_data["field"] = "added_photos"
   
   return INPUT

def change_submit(update: Update, context: CallbackContext):
    index = context.user_data.get("added_index")
    name = context.user_data.get("added_name")
    region = context.user_data.get("added_region")
    price = context.user_data.get("added_price")
    photos = context.user_data.get("added_photos")
    
    if not index:
        text = "Index has not set"
        update.callback_query.answer(text)
        context.user_data["START_OVER"] = True
        
        return selection_fields(update, context)
    if not name:
        text = "Name has not set"
        update.callback_query.answer(text)
        context.user_data["START_OVER"] = True
        
        return selection_fields(update, context)
    if not region:
        text = "Region has not set"
        update.callback_query.answer(text)
        context.user_data["START_OVER"] = True
        
        return selection_fields(update, context)
    if not price:
        text = "Price has not set"
        update.callback_query.answer(text)
        context.user_data["START_OVER"] = True
        
        return selection_fields(update, context)
    if not photos:
        text = "Photos has not set"
        update.callback_query.answer(text)
        context.user_data["START_OVER"] = True
        
        return selection_fields(update, context)
    
    data = {
        "goods_index": index,
        "name": name,
        "region": region,
        "price": price,
        "images": photos
    }
    save_goods(data)
    
    text = "New item has been added.\nTo add more /add"
    update.callback_query.answer()
    update.callback_query.edit_message_text(text)
    
    return END
      
def save_input(update: Update, context: CallbackContext):
    """Save user input"""
    context.user_data[context.user_data["field"]] = update.message.text
    context.user_data["START_OVER"] = True
    
    return selection_fields(update, context)

def save_photo(update: Update, context: CallbackContext):
    """Save user photo"""
    context.user_data["START_OVER"] = True
    
    file = update.message.photo[-1].get_file()
    file_name = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S.jpg")
    file_path = os.path.join(IMAGES_PATH, file_name)
    file.download(file_path)
    
    context.user_data[context.user_data["field"]] = file_path
    
    return selection_fields(update, context)

