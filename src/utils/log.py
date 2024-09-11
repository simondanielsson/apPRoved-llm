"""Set up logging."""

import logging
import logging.config
from pathlib import Path

import yaml

from configs import CONFIGS_DIRECTORY

LOG_CONFIG = CONFIGS_DIRECTORY / "log.yaml"
LOG_FOLDER = "logs"


def read_logging_config(
    config_path: str | Path = LOG_CONFIG,
) -> dict[str, str]:
    """Read logging configuration.

    :param config_path: Path to file holding logging configuration.
    :return: Logging configuration.
    """
    path_ = Path(config_path)
    if path_.exists():
        with path_.open() as file_:
            return yaml.safe_load(file_.read())
    else:
        error_message = "Log config not found."
        raise FileNotFoundError(error_message)


def configure_logging(config_path: str | Path = LOG_CONFIG) -> logging.Logger:
    """Configure logging for application.

    :param config_path: Path to file holding logging configuration.
    :raises FileNotFoundError: When logging cannot be initialized.
    """
    # Ensure logs folder exists.
    Path(LOG_FOLDER).mkdir(exist_ok=True)

    # Configure logging.
    logging.config.dictConfig(read_logging_config(config_path))
    return logging.getLogger(__name__)
