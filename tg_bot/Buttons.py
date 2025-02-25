import Messages
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

CLOTHE_MESSAGE_BUTTONS = [
        [
            InlineKeyboardButton(Messages.NEXT_PRODUCT_BUTTON_TEXT, callback_data="NEXT_PRODUCT"),
            InlineKeyboardButton(Messages.SEARCH_ANOTHER_ITEM_BUTTON_TEXT, callback_data="SEARCH_ANOTHER"),
        ],
        [
            InlineKeyboardButton(Messages.FOUND_ITEM_BUTTON_TEXT, callback_data="DONE"),
        ],
        [
              InlineKeyboardButton(Messages.NEW_UPLOAD_BUTTON_TEXT, callback_data="UPLOAD_NEW"),
        ]
    ]
