import json
import logging
import os
from os.path import isdir

"""
Module to manage file access.
"""

logger: logging.Logger = logging.getLogger()


class ConfigPathException(Exception):
    pass


class ConfigController:
    """
    Class to manage file access.
    """

    def __init__(self, path: str) -> None:
        """
        Constructor.

        Args:
            path (str): Path to the file.
        """
        self.file_path = path

    def _validate_path(self, file_path: str, is_dir: bool = False) -> bool:
        """
        Ensures the given file path is valid.

        Args:
            file_path (str): Path to the file/directory to check.
            is_dir (bool): Whether or not the target is a directory.

        Returns:
            bool: Whether or not the target is found.

        """
        logger.debug(f"Checking if the following path exists: {file_path}")
        if not is_dir:
            if not os.path.exists(file_path):
                logger.error("Failed to find the file.")
                return False
        elif not os.path.isdir(file_path):
            logger.error("Failed to find the directory.")
            return False

        return True

    def get_file_content(self) -> dict:
        """
        Gets the JSON content of the given file and returns it as a dictionary.

        Returns:
            dict: Parsed content of the config file.
        """
        logger.debug("Getting file content.")
        if self._validate_path(self.file_path):
            with open(self.file_path, "r", encoding="UTF-8") as config:
                return json.load(config)
        logger.error("Will raise an exception since the file couldn't be loaded.")
        raise ConfigPathException(f"File path is invalid: {self.file_path}")

    def write_file_content(self, content: dict) -> None:
        """
        Writes new JSON content to the configuration file.

        Args:
            content (dict): New content for the file.
        """
        directory: str = os.path.dirname(self.file_path)
        if not self._validate_path(directory, True):
            os.makedirs(directory)

        with open(self.file_path, "w", encoding="UTF-8") as config:
            json.dump(content, config)
