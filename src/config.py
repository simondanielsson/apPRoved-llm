"""Module to store the API's global config."""

from dotenv import load_dotenv

from src.utils.config import load_config
from configs import CONFIGS_DIRECTORY

# Load environment variables.
load_dotenv()

# Load configuration.
general_config_path = CONFIGS_DIRECTORY / "general.yaml"

config = load_config(
    [
        general_config_path,
    ],
)
