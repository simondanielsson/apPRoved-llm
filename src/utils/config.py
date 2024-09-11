"""Configuration loader."""

from collections import defaultdict
from os import environ
from pathlib import Path
from string import Template

import yaml
from box import Box


def load_config(config_paths: list[Path]) -> Box:
    """Load config from file.

    If file is not provided, default config is loaded.
    :param config_paths: Paths to config.
    :return: Boxed config.
    """
    config: dict = {}
    for config_path in config_paths:
        path_ = Path(config_path)
        if path_.exists():
            with path_.open() as file_:
                config = _update_config(yaml.safe_load(file_.read()), config)
        else:
            error_message = f"'{config_path}' not found, configuration is not loaded."
            raise FileNotFoundError(error_message)
    config = Box(config)
    environment_variables = defaultdict(lambda: "", environ)
    return _resolve_environment_variables(config, environment_variables)


def _update_config(source: dict, target: dict) -> dict:
    """Update nested dictionaries recursively.

    This happens in an append-overwrite manner:
    - Append if full key is unseen (e.g. parent.child).
    - Override if full key already exists in target.

    :param source: Source of new keys and values.
    :param target: Existing mapping to update with source.
    :return: Combination of both source and target.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # Recurse if the value in source is a nested dictionary.
            # Required to prevent overriding a key in full.
            # Instead go down the nesting, add the new keys,
            # and override the overlapping ones.
            target[key] = _update_config(value, target.get(key, {}))
        else:
            # Reached lowest level in recursion, set key to value.
            target[key] = value
    return target


def _resolve_environment_variables(config: Box, environment_variables: dict) -> Box:
    """Update config with values read from the environment.

    Compliant config values correspond to the format: ${NAME_OF_ENVIRONMENT_VARIABLE}.
    Default to empty string if the environment variable does not exist on the system.

    :param config: Config for the pipeline with environment variable placeholders.
    :param environment_variables: Dictionary holding the environment variables.
    :return: Config for the pipeline without environment variable placeholders.
    """
    for key, value in config.items():
        if isinstance(value, dict):
            _resolve_environment_variables(value, environment_variables)
        elif isinstance(value, list):
            config[key] = [
                (
                    Template(item).substitute(environment_variables)
                    if "${" in str(item)
                    else item
                )
                for item in value
            ]
        elif isinstance(value, str) and "${" in value:
            config[key] = Template(value).substitute(environment_variables)
    return config
