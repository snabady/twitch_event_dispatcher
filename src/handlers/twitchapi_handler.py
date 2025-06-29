import logging
from utils import log

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)  

def handle_follower_count(event: dict):
    event_data = event.get("event_data")
    follower_count = event_data.get("total_follower")
    # -> ins file schreiben damit obs richtig displayed
    logger.info(f"total follower: {follower_count}")

