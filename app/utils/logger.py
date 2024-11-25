from loguru import logger

logger.add("locality_app.log", rotation="10 MB")
