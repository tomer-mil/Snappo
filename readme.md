# Snappo - AI-Powered Fashion Search Telegram Bot 👗🔍

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Snappo is a Telegram bot that uses computer vision to identify clothing items in photos and helps users find similar products available for purchase online. Simply send a photo of an outfit, select which clothing item you're interested in, and Snappo will search for matching products!

![Snappo Bot Demo](https://via.placeholder.com/720x400?text=Snappo+Bot+Demo)

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [APIs Used](#apis-used)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- 📸 **Clothing Detection**: Automatically identifies different clothing items in photos
- 👗 **Multiple Item Support**: Detects and separates multiple clothing items (jackets, pants, dresses, etc.)
- 🔍 **Visual Search**: Finds visually similar clothing products using AI
- 🛍️ **Direct Shopping**: Provides instant purchase links to buy the exact items you're looking for
- 💬 **Interactive UI**: Easy-to-use Telegram interface with buttons for navigation
- 💰 **Price Information**: Displays pricing information for all found products

## How It Works

1. User sends a clothing photo to the Snappo Telegram bot
2. The bot processes the image using SegFormer to detect and extract clothing items
3. User selects which clothing item they want to find
4. The bot performs a visual search using the LykDat API
5. Results are presented with product images, prices, and direct purchase links
6. Users can immediately buy the exact items they're looking for with just a click
7. User can browse through results or search for different items

## Prerequisites

- Python 3.8 or higher
- Telegram account
- The following API keys:
  - Telegram Bot API token (from [BotFather](https://t.me/botfather))
  - [LykDat API](https://lykdat.com/api-documentation) key
  - [SerpApi](https://serpapi.com/) key
- PyTorch 2.5.1+
- CUDA-compatible GPU (recommended for faster processing)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tomer-mil/snappo.git
   cd snappo-bot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the segmentation model (this happens automatically on first run)

## Configuration

The bot is configured using environment variables:

1. Set up the following environment variables:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   LYKDAT_API_KEY=your_lykdat_api_key
   SERPAPI_KEY=your_serpapi_key
   ```

2. You can set these environment variables using a `.env` file or through your hosting provider's configuration panel

3. The application will automatically load these values when started

## Usage

The Snappo Bot is already running and available on Telegram!

### User Instructions

1. Start a conversation with [@SnappoTelegramBot](https://t.me/SnappoTelegramBot) on Telegram
2. You can either send a text message to start the conversation or directly send a photo containing clothing items
3. The bot will process the image and display buttons for each detected clothing item
4. Select the item you're interested in
5. Browse through similar products using the navigation buttons
6. Click on the purchase link to buy the product
7. Choose to search for another item or upload a new photo

### Navigation Commands

- **Next product ➡️**: Shows the next matching product
- **Search another item 🔄**: Returns to the clothing item selection
- **That's what I was looking for! 🎉**: Completes the search
- **Never mind, let me upload a new photo 📸**: Starts over with a new photo

## Project Structure

- `bot_api.py`: Main Telegram bot implementation
- `search_engine.py`: Coordinates search functionality
- `segmorfer_b2_clothes.py`: Clothing segmentation using AI
- `lykdat_api.py`: Visual similarity search API client
- `serp_api.py`: Text-based product search API client
- `Product.py`: Product data model
- `Constants.py`: Configuration constants
- `Messages.py`: User-facing text messages
- `Buttons.py`: UI button definitions
- `response_parser.py`: Standardizes API responses
- `response_enum.py`: Enumeration for API field mapping

## APIs Used

### 1. Telegram Bot API
Used for creating the conversational interface via a Telegram bot.

### 2. LykDat API
Visual search API that finds clothing items based on image similarity.

### 3. SerpApi
Google Shopping search API used as a fallback when visual search doesn't yield good results.

### 4. HuggingFace Transformers
Used for the SegFormer model that detects and segments clothing items in images.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Project created by [Your Name]

- **GitHub**: [tomer-mil](https://github.com/tomer-mil), [zoeyanai](https://github.com/zoeyanai), [YotamShekrelTau](https://github.com/YotamShekrelTau), [LiorBodner](https://github.com/LiorBodner)


For bug reports and feature requests, please open an issue on GitHub.

---

Made with ❤️ using Python and AI