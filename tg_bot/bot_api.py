from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from segmorfer_b2_clothes import get_clothes_from_image
import io
from image_processor import search_image
import json

user_products = {}
user_current_index = {}
current_clothe_type = ""
clothes_types = []
current_clothe_index = 0
current_clothe_type_index = 0

# ZOE_BOT_API_KEY = "7908756148:AAFBaJpnQCLW4F5wuETs5NpdhfP6J0GByjo"
BOT_API_KEY = "7596674915:AAF2VwAllFfBHTIIVRd2TYtU-GQ6pLiW04g"
async def find_products_from_image(photo_bytes, is_pil_image=False):
    # Load mock results from JSON file
    global user_products
    # try:
    #     with open('/Users/tomer.mildworth/Documents/University/Ecommerce/ecommerce/tg_bot/mock_results.json', 'r') as f:
    #         user_products = json.loads(f.read())
    #         # return json.loads(f.read())
    # except FileNotFoundError:
    #     return json.dumps({"error": "Mock results file not found"})
    return search_image(photo_bytes, is_pil_image)



# Handle photo messages
async def handle_photo(update, context) -> None:
    global clothes_types
    if not update.message.photo:
        await update.message.reply_text("Please send a valid photo.")
        return
    await update.message.reply_text("Snapping...")
    # Get the photo
    photo = update.message.photo[-1]  # Get the best quality photo
    photo_file = await context.bot.get_file(photo.file_id)  # Await the coroutine
    photo_bytes = io.BytesIO(await photo_file.download_as_bytearray())  # Await download

    clothes = get_clothes_from_image(photo_bytes)
    user_products.clear()  # Clear previous results
    # for clothe in clothes:
    #     clothes_types.append(clothe['clothe_type'])
    #     products = await find_products_from_image(clothe['clothe_type'])
    #     user_products[clothe['clothe_type']] = products

    await process_clothes(clothes)

    # products = await find_products_from_image(photo_bytes)

    await show_product(update, context)
    # await update.message.reply_text(products)

async def process_clothes(clothes):
    global clothes_types, user_products
    for clothe in clothes:
        clothes_types.append(clothe['clothe_type'])
        products = await find_products_from_image(clothe['image'], is_pil_image=True)
        user_products[clothe['clothe_type']] = json.loads(products)

async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_clothe_index
    global current_clothe_type
    # if current_clothe_index >= len(user_products[current_clothe_type]) or current_clothe_type_index >= len(clothes_types):
    #     await update.effective_chat.send_message("No more products to show!")
    #     return
    clothe_type = clothes_types[current_clothe_type_index]
    product = user_products[clothe_type][current_clothe_index]

    # Create keyboard with "Next" button and product link
    keyboard = [
        [InlineKeyboardButton("🛒 Buy Now", url=product['product_link'])],
        [InlineKeyboardButton("💲 Price: " + product['price'], callback_data='price')],
        [InlineKeyboardButton("➡️ Next Product", callback_data='next')],
        [InlineKeyboardButton("👚 Next Clothe", callback_data='clothe')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send product image with caption and buttons
    await update.effective_chat.send_photo(
        photo=product['thumbnail'],
        caption=f"Product {current_clothe_index + 1} of {len(user_products)}",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_clothe_index
    global current_clothe_type_index
    query = update.callback_query

    if query.data == 'next':
        current_clothe_index += 1
        await query.answer()
        await show_product(update, context)
    elif query.data == 'clothe':
        current_clothe_index = 0
        current_clothe_type_index += 1
        await query.answer()
        await show_product(update, context)


# Start command
async def start(update, context) -> None:
    await update.message.reply_text("Hey there, I'm Snappo!\nSend me a picture, and I'll find you the best match to purchase online 🛒")


# Main function
def main():

    application = Application.builder().token(BOT_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()


if __name__ == "__main__":
    main()
