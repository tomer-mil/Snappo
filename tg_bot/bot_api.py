from telegram import Update, Bot
from telegram.ext import Updater, Application, CommandHandler, MessageHandler, filters
from PIL import Image
from BLIP import generate_detailed_caption
import io
import requests

# BOT_API_KEY = "7908756148:AAFBaJpnQCLW4F5wuETs5NpdhfP6J0GByjo"
BOT_API_KEY = "7596674915:AAF2VwAllFfBHTIIVRd2TYtU-GQ6pLiW04g"
async def process_image_and_return_url(update: Update, image) -> str:
    # Item detection will happen here
    # caption = generate_detailed_caption(image.file_path)
    # await update.message.reply_text(caption)
    pass



# Handle photo messages
async def handle_photo(update, context) -> None:
    if not update.message.photo:
        await update.message.reply_text("Please send a valid photo.")
        return

    # Get the photo
    photo = update.message.photo[-1]  # Get the best quality photo
    photo_file = await context.bot.get_file(photo.file_id)  # Await the coroutine

    # caption = generate_detailed_caption(photo_file.file_path)

    # TODO: Pass the photo to the serpAPI
    await process_image_and_return_url(photo_file)
    photo_bytes = io.BytesIO(await photo_file.download_as_bytearray())  # Await download

    # Open the image and process it
    with Image.open(photo_bytes) as img:
        item_url = await process_image_and_return_url(img)

    # Send the result back as text
    await update.message.reply_text(item_url)


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
