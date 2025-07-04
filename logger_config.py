import logging
import sys
from pythonjsonlogger import jsonlogger

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# JSON log formatter
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d'
)
logHandler.setFormatter(formatter)
logger.handlers = [logHandler]

# Example usage:
# logger.info('App started', extra={'user': 'system'})
# logger.error('An error occurred', exc_info=True)
