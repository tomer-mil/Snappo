from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from PIL import Image
from BLIP import generate_detailed_caption
from image_processor import search_image
import io
import json
import requests

user_products = {}
user_current_index = {}
current_index = 0

# ZOE_BOT_API_KEY = "7908756148:AAFBaJpnQCLW4F5wuETs5NpdhfP6J0GByjo"
BOT_API_KEY = "7596674915:AAF2VwAllFfBHTIIVRd2TYtU-GQ6pLiW04g"
async def find_products_from_image(photo_bytes):
    # Load mock results from JSON file
    global user_products
    try:
        with open('/Users/tomer.mildworth/Documents/University/Ecommerce/ecommerce/tg_bot/mock_results.json', 'r') as f:
            user_products = json.loads(f.read())
            # return json.loads(f.read())
    except FileNotFoundError:
        return json.dumps({"error": "Mock results file not found"})
    # return search_image(photo_bytes)



# Handle photo messages
async def handle_photo(update, context) -> None:
    if not update.message.photo:
        await update.message.reply_text("Please send a valid photo.")
        return
    await update.message.reply_text("Snapping...")
    # Get the photo
    photo = update.message.photo[-1]  # Get the best quality photo
    photo_file = await context.bot.get_file(photo.file_id)  # Await the coroutine
    photo_bytes = io.BytesIO(await photo_file.download_as_bytearray())  # Await download

    products = await find_products_from_image(photo_bytes)
    await show_product(update, context)
    # await update.message.reply_text(products)


async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_index
    if current_index >= len(user_products):
        await update.effective_chat.send_message("No more products to show!")
        return

    product = user_products[current_index]

    # Create keyboard with "Next" button and product link
    keyboard = [
        [InlineKeyboardButton("🛒 Buy Now", url=product['product_link'])],
        [InlineKeyboardButton("💲 Price: " + product['price'], callback_data='price')],
        [InlineKeyboardButton("➡️ Next Product", callback_data='next')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send product image with caption and buttons
    await update.effective_chat.send_photo(
        photo=product['thumbnail'],
        caption=f"Product {current_index + 1} of {len(user_products)}",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_index
    query = update.callback_query

    if query.data == 'next':
        current_index += 1
        await query.answer()
        await show_product(update, context)

# Start command
async def start(update, context) -> None:
    await update.message.reply_text("Hey there, I'm Snappo!\nSend me a picture, and I'll find you the best match to purchase online 🛒")


# Main function
def main():

    # updater = Updater(token=BOT_API_KEY)
    # dispatcher = updater.dispatcher

    application = Application.builder().token(BOT_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()


if __name__ == "__main__":
    main()
