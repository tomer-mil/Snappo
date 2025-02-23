import logging
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

from segmorfer_b2_clothes import ClothesSegmorfer

# initialize logging for tracking the bot activity
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

BOT_API_KEY = "7926543787:AAEItPsl47bDrLs_uCCMK0zhjktl8MjcYwg"
tomer_and_zoe = False

# === STATES ===
WAITING_PHOTO = 0
WAITING_ITEM_SELECTION = 1
SHOWING_PRODUCT = 2

# In-memory storage for user data (per chat)
user_sessions = {}

async def run_segmorfer(image):
    if tomer_and_zoe:
        segmorfer = ClothesSegmorfer(image_bytes=image)
        return segmorfer.get_clothes_from_image()

    return ["hat", "upper-clothes", "pants"]  # Dummy data


# === PLACEHOLDERS FOR TOMER & ZOE FUNCTIONS ===
# the function for the searching of the clothing item (include fallbacks)
# get as arg the clothing type
# replcace with the new 'process_clothes' function
def search_clothing(clothing_type):
    """
    Dummy search function:
    Returns a list of product dicts, each with keys: 'image_url', 'name', 'price', 'link'
    """
    # TODO: Replace with your Lykdat or custom API call
    mock_products = [
        {
            "image_url": "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcRoWU5J_ZAcVUnFMLPvuRm1dPbMD6bb8dedFw01WI-qhP8fqvgjrrrbqCPGoRrU2R7DCRllsrrLgBkIKCmZVD8p9li0R6RMRO1BxKseMHU84GDtWYy9Pl1tCYD3dg18f2OC9qFq5p9IBKM&usqp=CAc",
            "name": f"Sample {clothing_type} #1",
            "price": "40",
            "currency": "USD",
            "link": "https://example.com/product1"
        },
        {
            "image_url": "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcRoWU5J_ZAcVUnFMLPvuRm1dPbMD6bb8dedFw01WI-qhP8fqvgjrrrbqCPGoRrU2R7DCRllsrrLgBkIKCmZVD8p9li0R6RMRO1BxKseMHU84GDtWYy9Pl1tCYD3dg18f2OC9qFq5p9IBKM&usqp=CAc",
            "name": f"Sample {clothing_type} #2",
            "price": "50",
            "currency": "USD",
            "link": "https://example.com/product2"
        },
        {
            "image_url": "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcRoWU5J_ZAcVUnFMLPvuRm1dPbMD6bb8dedFw01WI-qhP8fqvgjrrrbqCPGoRrU2R7DCRllsrrLgBkIKCmZVD8p9li0R6RMRO1BxKseMHU84GDtWYy9Pl1tCYD3dg18f2OC9qFq5p9IBKM&usqp=CAc",
            "name": f"Sample {clothing_type} #3",
            "price": "60",
            "currency": "USD",
            "link": "https://example.com/product3"
        }
    ]
    return mock_products

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
        await update.message.reply_text(
            "👋 Hello and welcome to Snappo Bot! 🎉\n\n"
            "Send me a photo of your outfit, and I'll help you find similar products! 🛍️📸"
        )

    # Move to waiting for photo
    return WAITING_PHOTO


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Called when the user sends a photo.
    Processes the image, extracts clothing items, and asks the user to choose one.
    """
    chat_id = update.effective_chat.id
    user_sessions.setdefault(chat_id, {})

    # Acknowledge receipt
    await update.message.reply_text("Such a nice outfit!👗\n\nLet me process the photo... 📸")

    try:
        # Download photo as bytes (in memory)
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        # Run Segmorfer with image bytes
        clothes = await run_segmorfer(image_bytes)  # Replacing segment_clothes()

        if not clothes:
            # No items found
            await update.message.reply_text(
                "Something went wrong. 😞\nI couldn't detect clothing in that photo. "
                "Please try again with another photo. 📸"
            )
            return WAITING_PHOTO

        # Store detected clothing items in user session
        user_sessions[chat_id]["clothes"] = clothes
        user_sessions[chat_id]["products"] = {}  # Will store matching products

        # Ask user which clothing item to search for
        keyboard = [
            [InlineKeyboardButton(item, callback_data=f"ITEM_{item}")]
            for item in clothes
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👗 I detected these clothing items in the photo. \n\nWhich one do you want to search for? 🛍️",
            reply_markup=reply_markup
        )
        return WAITING_ITEM_SELECTION

    except Exception as e:
        logging.error(f"Error processing photo: {e}")
        await update.message.reply_text(
            "Something went wrong. 😞\nPlease try again with another photo. 📸"
        )
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
        chosen_item = query.data.replace("ITEM_", "")
        user_data["chosen_item"] = chosen_item

        # Let user know we are searching
        await query.message.reply_text(
            "🎉 What a great choice! 🛍️\n\nGive me a few seconds to find a similar product for you to purchase! 🔍"
        )

        # Search for products
        products = search_clothing(chosen_item)
        user_data["products"][chosen_item] = products
        user_data["current_product_index"] = 0

        # Show the first product
        return await show_product(update, context)

    else:
        # Shouldn't happen if coded properly
        await query.message.reply_text("❌ Invalid selection, please try again. ❌")
        return WAITING_ITEM_SELECTION


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
    chosen_item = user_data.get("chosen_item")
    products = user_data.get("products", {}).get(chosen_item, [])
    current_index = user_data.get("current_product_index", 0)

    if not products:
        # Edge case, no product found
        if query:
            await query.message.reply_text(
                "😞 Sorry, I couldn't find any products for that item. "
                "Please send a new photo and I'll try again! 📸"
            )
        return WAITING_PHOTO

    # Keep index in range
    current_index = current_index % len(products)
    user_data["current_product_index"] = current_index

    product = products[current_index]
    product_img = product["image_url"]
    product_name = product["name"]
    product_price = product["price"]
    product_currency = product["currency"]
    product_link = product["link"]

    # Build the reply text
    text_msg = (
        f"👗 **{product_name}**\n\n"
        f"💲 **Price:** {product_price} {product_currency}\n\n"
        f"[🔗 **Purchase Link**]({product_link})\n\n"
        f"🛍️ Happy Shopping! 🎉"
    )

    # Buttons
    keyboard = [
        [
            InlineKeyboardButton("Next product ➡️", callback_data="NEXT_PRODUCT"),
            InlineKeyboardButton("Search another item 🔄", callback_data="SEARCH_ANOTHER"),
        ],
        [
            InlineKeyboardButton("That's what I was looking for! 🎉", callback_data="DONE"),
        ],
        [
              InlineKeyboardButton("Never mind, let me upload a new photo 📸", callback_data="UPLOAD_NEW"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edit current message or send a new one
    if query:
        try:
            await query.message.delete()
        except:
            pass

        # Send a new message with product photo
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=product_img,
            caption=text_msg,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return SHOWING_PRODUCT
    else:
        # If not a callback, just send a new message
        await update.message.reply_photo(
            photo=product_img,
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
        clothes = user_data.get("clothes", [])
        if not clothes:
            await query.message.reply_text(
                "No other items found. Please send a new photo."
            )
            return WAITING_PHOTO

        # Show clothing options again
        keyboard = [
            [InlineKeyboardButton(item, callback_data=f"ITEM_{item}")] 
            for item in clothes
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Which clothing item do you want to search for?",
            reply_markup=reply_markup
        )
        return WAITING_ITEM_SELECTION

    elif query.data == "DONE":
        # Reset flow
        await query.message.reply_text(
            "🎉 Awesome! I'm glad I could help! 😊\n\n"
            "Feel free to send me another picture anytime to search for more items. 📸🛍️"
        )
        # Clear session or partially reset
        user_sessions[chat_id]["current_product_index"] = 0
        return WAITING_PHOTO

    elif query.data == "UPLOAD_NEW":
    # Reset flow and ask the user to send a new photo
        await query.message.reply_text(
            "No worries! 😊\nSend me a new photo whenever you're ready. 📸"
        )
        # Clear session or partially reset
        user_sessions[chat_id]["current_product_index"] = 0
        return WAITING_PHOTO

    else:
        await query.message.reply_text("Unknown option.")
        return SHOWING_PRODUCT


def main():
    application = Application.builder().token(BOT_API_KEY).build()

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
