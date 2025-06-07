from loguru import logger

from core.config import settings

logger.remove()

logger.add(
    settings.LOG_FILE,
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} | {message}"
)

logger.add(
    sink=lambda message: print(message, end=''),
    level='INFO'        
)

root = logger
