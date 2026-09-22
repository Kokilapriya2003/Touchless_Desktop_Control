import logging
import os

def setup_logger():
    """Configures the application logger."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('TouchlessControl')
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler('logs/touchless.log')
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

logger = setup_logger()
