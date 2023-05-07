#!/usr/bin/env python3
import argparse
import logging
from logging.handlers import RotatingFileHandler


CONFIG_FILE: str = "~/.config/rss_to_masto/config.json"
WATERMARK_FILE: str = "~/.config/rss_to_maso/watermark.json"
DEFAULT_LOG: str = "/tmp/rss_to_masto.log"
MAX_LOG_SIZE: int = 5 * 1024 * 1024

def main(args: dict) -> None:
    """
    Main entrypoint.

    Args:
        args (dict): CLI arguments.
    """
    logger.info("Starting a new run to sync RSS to Mastodon.")
    logger.info("RSS sync to Mastodon complete.")

if __name__ == "__main__":
    desc: str = "Syncs an RSS feed to Mastodon."
    arg_parser: argparse.ArgumentParser = argparse.ArgumentParser(description=desc)
    arg_parser.add_argument(
        "-d", "--debug",
        action="store_true",
        required=False
    )
    arg_parser.add_argument(
        "-l", "--log",
        action="store",
        required=False
    )
    arg_parser.add_argument(
        "-c", "--config",
        action="store_true",
        required=False
    )
    arg_parser.add_argument(
        "-f", "--feed",
        action="store",
        required=True
    )
    arg_dict: dict = vars(arg_parser.parse_args())

    logger: logging.Logger = logging.getLogger()
    if arg_dict.get("debug"):
        logger.setLevel("DEBUG")
    else:
        logger.setLevel("INFO")

    log_path: str = DEFAULT_LOG
    if arg_dict.get("log"):
        log_path = arg_dict["log"]

    format_string: str = "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
    log_format: logging.Formatter = logging.Formatter(format_string)
    rot_hand = RotatingFileHandler(
        filename=log_path,
        mode="a",
        maxBytes=MAX_LOG_SIZE,
        backupCount=2,
        encoding=None,
        delay=False
    )
    rot_hand.setFormatter(log_format)
    logger.addHandler(rot_hand)
    main(arg_dict)

