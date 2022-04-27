import logging
from discord_handler import DiscordHandler
import os


def get_logger(
    name: str = __name__, log_level: int = logging.DEBUG, log_file: str = None
) -> logging.Logger:
    logger = logging.getLogger(name)

    # Check if logger already has handlers
    if not len(logger.handlers):
        logger.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")

        # stdout logger
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_level)
        logger.addHandler(stream_handler)

        # file logger
        if log_file is not None:

            # Make sure the path exist
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)

        # Discord logger
        discord_webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        if discord_webhook_url is not None:
            discord_handler = DiscordHandler(
                discord_webhook_url, emit_as_code_block=False, max_size=20000
            )
            discord_handler.setLevel(logging.CRITICAL)
            discord_handler.setFormatter(formatter)
            logger.addHandler(discord_handler)
        else:
            logger.warning("Discord webhook url not found for logger")

    return logger


def get_common_logger(name: str = "pipeline"):
    log_filename = f"pipeline/logs/{name}.log"
    LOG_LEVEL = logging.DEBUG  # Log level for stdout
    logger = get_logger(name, LOG_LEVEL, log_filename)
    return logger
