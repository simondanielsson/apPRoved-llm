"""Module to store the API's global config."""

from dotenv import load_dotenv

from configs import CONFIGS_DIRECTORY
from src.utils.config import load_config

# Load environment variables.
load_dotenv()

# Load configuration.
general_config_path = CONFIGS_DIRECTORY / "general.yaml"

config = load_config(
    [
        general_config_path,
    ],
)
