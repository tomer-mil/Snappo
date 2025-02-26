import os
import json
from pathlib import Path

# Default environment variable names
LYKDAT_API_KEY_ENV = "LYKDAT_API_KEY"
SERPAPI_KEY_ENV = "SERPAPI_KEY"
TELEGRAM_BOT_API_KEY_ENV = "TELEGRAM_BOT_API_KEY"

# Config file location
CONFIG_DIR = Path.home() / ".snappo"
CONFIG_FILE = CONFIG_DIR / "config.json"


def set_api_key(key_name, value):
	"""Set an environment variable for an API key."""
	os.environ[key_name] = value


def get_api_key(key_name, default=None):
	"""Get an API key from environment variables."""
	return os.environ.get(key_name, default)


def check_api_keys():
	"""Check if all required API keys are set."""
	required_keys = [
		LYKDAT_API_KEY_ENV,
		SERPAPI_KEY_ENV,
		TELEGRAM_BOT_API_KEY_ENV
	]

	missing_keys = [key for key in required_keys if not get_api_key(key)]
	return len(missing_keys) == 0, missing_keys


def save_keys_to_config():
	"""Save the current API keys to a config file."""
	# Make sure the directory exists
	os.makedirs(CONFIG_DIR, exist_ok=True)

	# Get current keys
	config = {
		LYKDAT_API_KEY_ENV: get_api_key(LYKDAT_API_KEY_ENV, ""),
		SERPAPI_KEY_ENV: get_api_key(SERPAPI_KEY_ENV, ""),
		TELEGRAM_BOT_API_KEY_ENV: get_api_key(TELEGRAM_BOT_API_KEY_ENV, "")
	}

	# Save to file
	with open(CONFIG_FILE, "w") as f:
		json.dump(config, f)

	return True


def load_keys_from_config():
	"""Load API keys from the config file if it exists."""
	if not CONFIG_FILE.exists():
		return False

	try:
		with open(CONFIG_FILE, "r") as f:
			config = json.load(f)

		for key, value in config.items():
			if value:  # Only set if value is not empty
				set_api_key(key, value)

		return True
	except (json.JSONDecodeError, IOError):
		return False
