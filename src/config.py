"""Module to store the API's global config."""

import os

from dotenv import load_dotenv

from configs import CONFIGS_DIRECTORY
from src.utils.config import load_config

# Load environment variables.
env_file = (
    ".env.production" if os.getenv("APP_ENV") == "production" else ".env.development"
)
load_dotenv(env_file)

# Load configuration.
general_config_path = CONFIGS_DIRECTORY / "general.yaml"

config = load_config(
    [
        general_config_path,
    ],
)
