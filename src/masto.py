"""
Controller for interfacing with Mastodon and the local Mastodon configuration
file.
"""
import json
import logging
import os
import requests

from urllib.parse import urlencode

from config_controller import ConfigController


logger: logging.Logger = logging.getLogger()


class MastodonCommException(Exception):
    """
    Class to handle Mastodon communication exceptions.
    """

    pass


class Mastodon:
    """
    Class to control interfacing with Mastodon.

    Attrs:
        _api_version (str): Current Mastodon API version.
        _client_name (str): Name of this client.
        _project_url (str): URL for this project's repo.
        _redirect_uris (str): Redirect URIs for Mastodon.
        _scopes (str): Scopes requested with Mastodon.
        client (Mastodon): Mastodon.py client object.
    """

    _api_version: str = "v1"
    _client_name: str = "RssToMasto"
    _project_url: str = "https://github.com/jfabry-noc/RssToMasto"
    _redirect_uris: str = "urn:ietf:wg:oauth:2.0:oob"
    _scopes: str = "read write push"

    def __init__(self, config_path: str) -> None:
        """
        Instantiates Mastodon controller.

        Args:
            config_path (str): Path to the config file.
        """
        self.config_path: str = config_path
        self.config: dict = {}

    def load_config(self) -> bool:
        if not os.path.isfile(self.config_path):
            logger.info("No config file found at: %s", self.config_path)
            logger.info("Prompting for config info.")
            self.create_config(self.config_path)
            return False
        else:
            file_controller: ConfigController = ConfigController(self.config_path)
            self.config = file_controller.get_file_content()
            return True

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
        if instance.endswith("/"):
            instance = instance[: len(instance) - 1]

        return f"https://{instance}"

    def create_app(self, api_base: str) -> tuple:
        """
        Registers a new application in Mastodon.

        Args:
            api_base (str): Base URL for this instance's API.
        """
        client_id: str = ""
        client_secret: str = ""
        form_data: dict = {
            "client_name": Mastodon._client_name,
            "redirect_uris": Mastodon._redirect_uris,
            "scopes": Mastodon._scopes,
            "website": Mastodon._project_url,
        }
        resp: requests.Response = requests.post(
            url=f"{api_base}/api/{self._api_version}/apps", data=form_data, timeout=30
        )

        if resp.ok:
            result: dict = json.loads(resp.content)
            client_id: str = result.get("client_id", "")
            client_secret: str = result.get("client_secret", "")
        else:
            print(f"Failed to register app with response code: {resp.status_code}")
            raise MastodonCommException

        if not client_id or not client_secret:
            print(f"Failed to retrieve client ID or secret!")
            raise MastodonCommException

        return (client_id, client_secret)

    def get_auth_code(self, client_id: str, api_base: str) -> str:
        """
        Obtains a user authentication code.

        Args:
            client_id (str): Client ID.
            api_base (str): Base URL for the instance.

        Returns:
            str: Authentication code.
        """
        url_params: dict = {
            "client_id": client_id,
            "scope": Mastodon._scopes,
            "redirect_uri": Mastodon._redirect_uris,
            "response_type": "code",
        }

        url: str = f"{api_base}/oauth/authorize" + "?" + urlencode(url_params)

        print(
            "Please go to the following URL in your browser. Then enter the access code you receive."
        )

        print(f"URL: {url}")

        code: str = input("Code: > ")

        return code

    def get_access_token(
        self, client_id: str, client_secret: str, auth_code: str, api_base: str
    ) -> str:
        """
        Gets the access token.

        Args:
            client_id (str): Client ID.
            client_secret (str): Client secret.
            auth_code (str): User authentication code.
            api_base (str): Base URL for the instance.

        Returns:
            str: Access token to store.
        """
        token: str = ""
        form_data: dict = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": Mastodon._redirect_uris,
            "grant_type": "authorization_code",
            "code": auth_code,
            "scope": Mastodon._scopes,
        }

        url: str = f"{api_base}/oauth/token"
        resp: requests.Response = requests.post(url=url, data=form_data, timeout=30)

        if resp.ok:
            result = json.loads(resp.content)
            token = result.get("access_token", "")
        else:
            print(
                f"Failed to get an access token with response code: {resp.status_code}"
            )
            raise MastodonCommException

        if not token:
            print("No access token was retrieved!")
            raise MastodonCommException

        return token

    def create_config(self, config_path: str) -> None:
        """
        Creates a new configuration file.

        Args:
            config_path (str): Path where the config file should leave.

        Returns:
            dict: Content of the loaded config file.
        """
        print(f"This process will create a new config file at: {config_path}")
        print(
            "Enter the domain name (e.g. mastodon.social) for your Mastodon instance."
        )
        instance: str = input("> ")
        instance = self.parse_instance(instance)

        client_resp: tuple = self.create_app(instance)
        auth_code: str = self.get_auth_code(client_resp[0], instance)
        access_token: str = self.get_access_token(
            client_resp[0], client_resp[1], auth_code, instance
        )

        config_content: dict = {"instance": instance, "token": access_token}

        file_controller: ConfigController = ConfigController(config_path)
        file_controller.write_file_content(config_content)

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
