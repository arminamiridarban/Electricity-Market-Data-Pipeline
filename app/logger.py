import logging

def get_logger(name: str):
    """
    Creates logger with the specified name, sets it to INFO level, and adds a StreamHandler with a standard formatter if it doesn't already have handlers.
    Input: name - the name of the logger (e.g., 'app.client')
    Output: configured logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    return logger