import logging


def get_logger(
    name: str = __name__, log_level: int = logging.DEBUG, log_file: str = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # stdout logger
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)
    logger.addHandler(stream_handler)

    # file logger
    if log_file is not None:
        import os

        # Make sure the path exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    return logger
