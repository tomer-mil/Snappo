from telegram_bot.handlers import setup_and_run_bot
from utils.env_manager import (
	set_api_key,
	get_api_key,
	LYKDAT_API_KEY_ENV,
	SERPAPI_KEY_ENV,
	TELEGRAM_BOT_API_KEY_ENV,
	check_api_keys,
	load_keys_from_config,
	save_keys_to_config
)


def validate_api_key(key, name):
	"""Basic validation for API keys."""
	if not key:
		print(f"Error: {name} cannot be empty")
		return False

	if len(key) < 10:  # Basic check for key length
		print(f"Warning: {name} seems too short. Please check if it's correct.")
		confirm = input("Continue anyway? (y/n): ").lower()
		return confirm == 'y'

	return True


def collect_api_keys():
	"""Collect API keys from the user through command line input."""
	print("=" * 50)
	print("Welcome to Snappo Bot!")
	print("Please enter your API keys to proceed:")
	print("=" * 50)

	while True:
		# Get Lykdat API key
		current_key = get_api_key(LYKDAT_API_KEY_ENV, "")
		display_key = f"...{current_key[-5:]}" if current_key else None
		prompt = f"\nLykdat API key{f' [current: {display_key}]' if display_key else ''}: "
		lykdat_key = input(prompt) or current_key

		if not validate_api_key(lykdat_key, "Lykdat API key"):
			continue
		set_api_key(LYKDAT_API_KEY_ENV, lykdat_key)

		# Get SerpAPI key
		current_key = get_api_key(SERPAPI_KEY_ENV, "")
		display_key = f"...{current_key[-5:]}" if current_key else None
		prompt = f"\nSerpAPI key{f' [current: {display_key}]' if display_key else ''}: "
		serpapi_key = input(prompt) or current_key

		if not validate_api_key(serpapi_key, "SerpAPI key"):
			continue
		set_api_key(SERPAPI_KEY_ENV, serpapi_key)

		# Get Telegram Bot API key
		current_key = get_api_key(TELEGRAM_BOT_API_KEY_ENV, "")
		display_key = f"...{current_key[-5:]}" if current_key else None
		prompt = f"\nTelegram Bot API key{f' [current: {display_key}]' if display_key else ''}: "
		telegram_key = input(prompt) or current_key

		if not validate_api_key(telegram_key, "Telegram Bot API key"):
			continue
		set_api_key(TELEGRAM_BOT_API_KEY_ENV, telegram_key)

		break

	# Ask if user wants to save the keys
	save_keys = input("\nSave these API keys for future use? (y/n): ").lower()
	if save_keys == 'y':
		save_keys_to_config()
		print("API keys saved to configuration file.")

	print("\nThank you! All API keys have been set.")


def main():
	# Try to load keys from config first
	config_loaded = load_keys_from_config()
	if config_loaded:
		print("API keys loaded from saved configuration.")

	# Check if API keys are set
	keys_are_set, missing_keys = check_api_keys()

	if not keys_are_set:
		collect_api_keys()

	# Run the bot
	setup_and_run_bot()


if __name__ == "__main__":
	main()
