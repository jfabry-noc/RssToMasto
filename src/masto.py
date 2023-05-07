import json
import logging
import os


logger: logging.Logger = logging.getLogger()

API_VERSION: str = "v1"

class Mastodon:
    """
    Class to control interfacing with Mastodon.

    Attrs:
        client (Mastodon): Mastodon.py client object.
    """
    def __init__(self, config_path: str) -> None:
        """
        Instantiates Mastodon controller.

        Args:
            config_path (str): Path to the config file.
        """
        config: dict = {}
        if not os.path.isfile(config_path):
            logger.info(f"No config file found at: {config_path}")
            logger.info("Prompting for config info.")
        if os.path.isfile(config_path):
            config = self.load_config(config_path)

    def parse_instance(self, instance: str) -> str:
        """
        Accepts a Mastodon instance from the user and cleans it.

        Args:
            instance (str): Instance as the user entered it.

        Returns:
            str: Cleaned instance.
        """
        instance = instance.strip()
        if instance.startswith("https://"):
            instance = instance[8:]
        elif instance.startswith("http://"):
            instance = instance[7:]

        return instance

    def create_app(self, api_base: str) -> None:
        """
        Registers a new application in Mastodon.

        Args:
            api_base (str): Base URL for this instance's API.
        """
        pass

    def create_config(self, config_path: str) -> dict:
        """
        Creates a new configuration file.

        Args:
            config_path (str): Path where the config file should leave.

        Returns:
            dict: Content of the loaded config file.
        """
        print(f"This process will create a new config file at: {config_path}")
        print("Enter the domain name (e.g. mastodon.social) for your Mastodon instance.")
        instance: str = input("> ")


    def validate_config(self, config: dict) -> bool:
        """
        Checks if the given configuration is valid.

        Args:
            config (dict): The loaded configuration.

        Returns:
            bool: Whether or not the config is valid.
        """
        if not config.get("instance") or not config.get("token"):
            return False
        return True

    def load_config(self, config_path) -> dict:
        """
        Loads an existing config file.

        Args:
            config_path (str): Path to the configuration file.

        Returns:
            dict: The current configuration.
        """
        content: dict = {}
        with open(config_path, "r") as config_file:
            content = json.load(config_file)

        return content
