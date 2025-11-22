import os
import logging
from src.utils import log,file_io

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)  

def handle_follower_count(event: dict):
    follower_text = os.getenv("FOLLOW_CNT_TEXT", "FOLLOW_CNT_TEXT")
    event_data = event.get("event_data")
    follower_text = follower_text.replace("{follower_count}", str(event_data.get("total_follower")))
    
    logger.info(f"total follower: {event_data.get("total_follower")}")
    
    file_io.write_file(os.getenv("FOLLOW_CNT_FILEPATH", "failed to laod dotenv FOLLOW_CNT_FILEPATH"),"w",follower_text)

def handle_sub_count(event: dict):
    event_data = event.get("event_data")
    sub_text = os.getenv("SUB_CNT_TEXT", "SUB_CNT_TEXT")
    sub_text = sub_text.replace("{sub_count}", str(event_data.get("total_subs")))
    file_io.write_file(os.getenv("SUB_CNT_FILEPATH"), "w", sub_text)
