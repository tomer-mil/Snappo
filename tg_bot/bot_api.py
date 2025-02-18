from telegram import Update, Bot
from telegram.ext import Updater, Application, CommandHandler, MessageHandler, filters
from PIL import Image
from BLIP import generate_detailed_caption
from image_processor import search_image
import io
import requests

# ZOE_BOT_API_KEY = "7908756148:AAFBaJpnQCLW4F5wuETs5NpdhfP6J0GByjo"
BOT_API_KEY = "7596674915:AAF2VwAllFfBHTIIVRd2TYtU-GQ6pLiW04g"
async def find_products_from_image(photo_bytes):
    return search_image(photo_bytes)



# Handle photo messages
async def handle_photo(update, context) -> None:
    if not update.message.photo:
        await update.message.reply_text("Please send a valid photo.")
        return

    # Get the photo
    photo = update.message.photo[-1]  # Get the best quality photo
    photo_file = await context.bot.get_file(photo.file_id)  # Await the coroutine
    photo_bytes = io.BytesIO(await photo_file.download_as_bytearray())  # Await download

    products = await find_products_from_image(photo_bytes)
    await update.message.reply_text(products)


# Start command
async def start(update, context) -> None:
    await update.message.reply_text("Send me a picture, and I'll analyze it and send back the results as text!")


# Main function
def main():

    # updater = Updater(token=BOT_API_KEY)
    # dispatcher = updater.dispatcher

    application = Application.builder().token(BOT_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling()
    # updater.run_polling()
    # application.idle()

if __name__ == "__main__":
    main()
