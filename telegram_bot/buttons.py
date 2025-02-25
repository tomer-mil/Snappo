import messages
from telegram import InlineKeyboardButton

CLOTHE_MESSAGE_BUTTONS = [
        [
            InlineKeyboardButton(messages.NEXT_PRODUCT_BUTTON_TEXT, callback_data="NEXT_PRODUCT"),
            InlineKeyboardButton(messages.SEARCH_ANOTHER_ITEM_BUTTON_TEXT, callback_data="SEARCH_ANOTHER"),
        ],
        [
            InlineKeyboardButton(messages.FOUND_ITEM_BUTTON_TEXT, callback_data="DONE"),
        ],
        [
              InlineKeyboardButton(messages.NEW_UPLOAD_BUTTON_TEXT, callback_data="UPLOAD_NEW"),
        ]
    ]
