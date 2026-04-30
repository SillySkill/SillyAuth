# ============================================
# SillyMD Backend - Logging Configuration
# ============================================

import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging():
    """Setup application logging"""

    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)

    # JSON formatter for production
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
