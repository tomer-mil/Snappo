from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image
import io


async def process_image_and_return_url(image) -> str:
    # Item detection will happen here
    pass


# Handle photo messages
async def handle_photo(update: Update, context) -> None:
    if not update.message.photo:
        await update.message.reply_text("Please send a valid photo.")
        return

    # Get the photo
    photo = update.message.photo[-1]  # Get the best quality photo
    photo_file = await context.bot.get_file(photo.file_id)  # Await the coroutine
    photo_bytes = io.BytesIO(await photo_file.download_as_bytearray())  # Await download

    # Open the image and process it
    with Image.open(photo_bytes) as img:
        item_url = await process_image_and_return_url(img)

    # Send the result back as text
    await update.message.reply_text(item_url)


# Start command
async def start(update: Update, context) -> None:
    await update.message.reply_text("Send me a picture, and I'll analyze it and send back the results as text!")


# Main function
def main():
    application = Application.builder().token("7908756148:AAFBaJpnQCLW4F5wuETs5NpdhfP6J0GByjo").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()


if __name__ == "__main__":
    main()
