import logging
from typing import Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
    ConversationHandler
)

from telegram_bot import messages, buttons
from utils.constants import TelegramBot as Constants
from core.search_engine import SearchEngine

# initialize logging for tracking the bot activity
logging.basicConfig(
    format=Constants.LOGGING_FORMAT,
    level=logging.INFO
)

BOT_API_KEY = "7596674915:AAF2VwAllFfBHTIIVRd2TYtU-GQ6pLiW04g"

# === STATES ===
WAITING_PHOTO = 0
WAITING_ITEM_SELECTION = 1
SHOWING_PRODUCT = 2

# In-memory storage for user data (per chat)
user_sessions = {}

async def extract_clothes_from_user_image(update, chat_id, image) -> Any:
    """
    Processes the user-uploaded image to extract clothing items.
    Stores detected clothing types in the user session.
    """
    user_sessions[chat_id]["search_engine"].extract_clothes_from_image(image)
    clothe_types = user_sessions[chat_id]["search_engine"].clothe_types

    if not clothe_types:
        # No items found
        await update.message.reply_text(messages.NO_ITEMS_FOUND_ERROR_MESSAGE)
        return WAITING_PHOTO

    # Store detected clothing items in user session
    user_sessions[chat_id]["clothe_types"] = clothe_types
    return WAITING_ITEM_SELECTION


def search_matching_products(chat_id, clothing_type):
    """
    Searches for products matching the detected clothing type.
    Returns a list of product dictionaries containing:
    - 'image_url'
    - 'name'
    - 'price'
    - 'link'
    """
    products = user_sessions[chat_id]["search_engine"].search_product_by_type(clothing_type)
    return products


# === HANDLERS ===

async def welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a welcome message automatically.
    This can be triggered on any first interaction or once per chat if desired.
    """
    chat_id = update.effective_chat.id
    # Track that we've welcomed this user (avoid spamming if they send multiple photos)
    if 'welcomed' not in user_sessions.get(chat_id, {}):
        user_sessions.setdefault(chat_id, {})['welcomed'] = True
        await update.message.reply_text(messages.WELCOME_MESSAGE)

    # Move to waiting for photo
    return WAITING_PHOTO


async def set_user_session_per_chat_id(chat_id: int):
    """
    Initializes user session with a SearchEngine instance for product searching.
    """
    user_sessions.setdefault(chat_id, {})
    user_sessions[chat_id]["search_engine"] = SearchEngine()
    user_sessions[chat_id]["products"] = {}  # Will store matching products
    clothe_types = user_sessions[chat_id]["search_engine"].clothe_types


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Called when the user sends a photo.
    Processes the image, extracts clothing items, and asks the user to choose one.
    """
    chat_id = update.effective_chat.id

    # Set session's SearchEngine and products dict
    await set_user_session_per_chat_id(chat_id=chat_id)

    # Acknowledge receipt
    await update.message.reply_text(messages.PHOTO_PROCESSING_MESSAGE)

    try:
        # Download photo as bytes (in memory)
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        await extract_clothes_from_user_image(update=update,
                                              chat_id=chat_id,
                                              image=image_bytes)  # Replacing segment_clothes()

        # Ask user which clothing item to search for
        keyboard = [
            [InlineKeyboardButton(clothe_type, callback_data=f"ITEM_{clothe_type}")]
            for clothe_type in user_sessions[chat_id]["clothe_types"]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            messages.DETECTED_CLOTHES_MESSAGE,
            reply_markup=reply_markup
        )
        return WAITING_ITEM_SELECTION

    except Exception as e:
        logging.error(f"{Constants.PHOTO_PROCESSING_ERROR_MESSAGE} {e}")
        await update.message.reply_text(messages.GENERAL_ERROR_MESSAGE)
        return WAITING_PHOTO


async def item_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the callback when the user selects a clothing item.
    Performs the product search and shows the first product.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    chat_id = query.message.chat_id
    user_data = user_sessions.setdefault(chat_id, {})

    # Parse clothing item
    if query.data.startswith("ITEM_"):
        chosen_clothe_type = query.data.replace("ITEM_", "")
        user_data["chosen_clothe_type"] = chosen_clothe_type

        # Let user know we are searching
        await query.message.reply_text(messages.CLOTHE_SELECTION_MESSAGE)

        # Search for products
        products = search_matching_products(chat_id=chat_id,
                                            clothing_type=chosen_clothe_type)

        user_data["products"][chosen_clothe_type] = products
        user_data["current_product_index"] = 0

        # Show the first product
        return await show_product(update, context)

    else:
        # Shouldn't happen if coded properly
        await query.message.reply_text(messages.INVALID_SELECTION_ERROR_MESSAGE)
        return WAITING_ITEM_SELECTION


def build_clothe_message(product):
    """
    Constructs the message containing product details.
    """
    return (
        f"👗 **{product.name}**\n\n"
        f"💲 **Price:** {product.price}{product.currency}\n\n"
        f"🔗 [**Purchase Link**]({product.url})\n\n"
        f"🛍️ Happy Shopping! 🎉"
    )


async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays the current product to the user, providing the Next, Search Another, or Confirm buttons.
    """
    # If triggered by callback
    if update.callback_query:
        query = update.callback_query
        chat_id = query.message.chat_id
    else:
        # If triggered in some other route (rare in this flow)
        chat_id = update.effective_chat.id
        query = None

    user_data = user_sessions.get(chat_id, {})
    chosen_clothe_type = user_data.get("chosen_clothe_type")
    products = user_data.get("products", {}).get(chosen_clothe_type, [])
    current_index = user_data.get("current_product_index", 0)

    if not products:
        # Edge case, no product found
        if query:
            await query.message.reply_text(messages.NO_PRODUCTS_FOUND_MESSAGE)

        return WAITING_PHOTO

    # Keep index in range
    current_index = current_index % len(products)
    user_data["current_product_index"] = current_index

    product = products[current_index]

    # Build the reply text
    text_msg = build_clothe_message(product=product)

    # Buttons
    reply_markup = InlineKeyboardMarkup(buttons.CLOTHE_MESSAGE_BUTTONS)

    # Edit current message or send a new one
    if query:
        try:
            await query.message.delete()
        except:
            pass

        # Send a new message with product photo
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=product.image_url,
            caption=text_msg,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return SHOWING_PRODUCT
    else:
        # If not a callback, just send a new message
        await update.message.reply_photo(
            photo=product.image_url,
            caption=text_msg,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return SHOWING_PRODUCT


async def product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the product navigation: Next product, Search another item, or Done.
    """
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    user_data = user_sessions.get(chat_id, {})

    if query.data == "NEXT_PRODUCT":
        # Show next product
        user_data["current_product_index"] += 1
        return await show_product(update, context)

    elif query.data == "SEARCH_ANOTHER":
        # Present the user with the clothing items again
        clothes = user_data.get("clothe_types", [])
        if not clothes:
            await query.message.reply_text(
                "No other items found. Please send a new photo."
            )
            return WAITING_PHOTO

        # Show clothing options again
        keyboard = [
            [InlineKeyboardButton(clothe_type, callback_data=f"ITEM_{clothe_type}")]
            for clothe_type in user_sessions[chat_id]["clothe_types"]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            messages.SEARCH_ANOTHER_CLOTHE_MESSAGE,
            reply_markup=reply_markup
        )
        return WAITING_ITEM_SELECTION

    elif query.data == "DONE":
        # Reset flow
        await query.message.reply_text(messages.FOUND_ITEM_RESPONSE_MESSAGE)

        # Clear session or partially reset
        user_sessions[chat_id]["current_product_index"] = 0
        return WAITING_PHOTO

    elif query.data == "UPLOAD_NEW":
        # Reset flow and ask the user to send a new photo
        await query.message.reply_text(messages.NEW_UPLOAD_RESPONSE_MESSAGE)

        # Clear session or partially reset
        user_sessions[chat_id]["current_product_index"] = 0
        return WAITING_PHOTO

    else:
        await query.message.reply_text("Unknown option")
        return SHOWING_PRODUCT


def main():
    """
    Initializes and starts the Telegram bot application.
    """
    application = Application.builder().token(BOT_API_KEY).build()
    application.bot_data["search_engine"] = SearchEngine()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo),
            MessageHandler(filters.ALL & ~filters.COMMAND, welcome_message),
        ],
        states={
            WAITING_PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo),
                MessageHandler(filters.TEXT, welcome_message),
            ],
            WAITING_ITEM_SELECTION: [
                CallbackQueryHandler(item_selection_callback, pattern=r"^ITEM_.*$"),
            ],
            SHOWING_PRODUCT: [
                CallbackQueryHandler(product_callback, pattern="^(NEXT_PRODUCT|SEARCH_ANOTHER|DONE|UPLOAD_NEW)$"),
            ],
        },
        fallbacks=[],
        per_chat=True,
        per_user=True,
    )

    application.add_handler(conv_handler)

    # Start the bot (polling)
    application.run_polling()


if __name__ == "__main__":
    main()
