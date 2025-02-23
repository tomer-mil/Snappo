from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from segmorfer_b2_clothes import ClothesSegmorfer
import io
from APIs.lykdat_api import search_lykdat


user_products = {}
user_current_index = {}
current_clothe_type = ""
clothes_types = []
current_clothe_index = 0
current_clothe_type_index = 0


BOT_API_KEY = "7596674915:AAF2VwAllFfBHTIIVRd2TYtU-GQ6pLiW04g"


async def send_text_reply(update, text):
    await update.message.reply_text(text)


async def run_segmorfer(image):
    segmorfer = ClothesSegmorfer(image_bytes=image)
    return segmorfer.get_clothes_from_image()


async def find_matching_products_from_user_image(user_clothe):
    global user_products
    # Load mock results from JSON file
    # try:
    #     with open('/Users/tomer.mildworth/Documents/University/Ecommerce/ecommerce/tg_bot/mock_results.json', 'r') as f:
    #         user_products = json.loads(f.read())
    #         # return json.loads(f.read())
    # except FileNotFoundError:
    #     return json.dumps({"error": "Mock results file not found"})
    # return json.loads(search_image(user_clothe, is_pil_image))
    return search_lykdat(pil_image=user_clothe)



# Handle photo messages
async def handle_photo(update, context) -> None:
    global clothes_types

    if not update.message.photo:
        await send_text_reply(update=update, text="Please send a valid photo.")
        return

    await send_text_reply(update=update, text="Snapping...")

    # Get the photo
    photo = update.message.photo[-1]  # Get the best quality photo
    photo_file = await context.bot.get_file(photo.file_id)  # Await the coroutine
    photo_bytes = io.BytesIO(await photo_file.download_as_bytearray())  # Await download

    extracted_clothes_list = await run_segmorfer(photo_bytes)

    await process_clothes(extracted_clothes_list)

    await show_product(update, context)

async def process_clothes(clothes):
    global clothes_types, user_products

    for clothe in clothes:
        # Add the clothe type to the list
        clothes_types.append(clothe['clothe_type'])

        # Find matching products for the clothe in lykdat
        matching_product = await find_matching_products_from_user_image(clothe['image'])

        # Add the lykdat results to the user products
        user_products[clothe['clothe_type']] = matching_product


async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_clothe_index, current_clothe_type

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
    await send_text_reply(update, text="Hey there, I'm Snappo!\nSend me a picture, and I'll find you the best match to purchase online 🛒")


# Main function
def main():

    application = Application.builder().token(BOT_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()


if __name__ == "__main__":
    main()
