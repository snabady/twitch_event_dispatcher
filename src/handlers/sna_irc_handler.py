import logging
from utils import log
from handlers import db_handler 


from dispatcher.event_dispatcher import post_event
#from baitgame.bait import FishGame
logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   

def handle_chat_event(event_data):
    logger.debug("handle_chat_event")

def handle_chat_command(event_data):
    logger.debug("handle_chat_command")
    logger.debug(f"event_data {event_data}")
    if event_data.get("event_data").get("cmd_name") == "bait":
        logger.debug("ajo it is a bait")
        post_event("fish_bait",event_data.get("event_data").get("user"))

    elif event_data.get("event_data").get("cmd_name")  =="followage":
        logger.debug("followage_command triggered")
        post_event("followage_command", event_data.get("event_data").get("user"))
    
    elif event_data.get("event_data".get("cmd_name")) == "sb":
        logger.debug("sb_command triggered")
       
    elif event_data.get("event_data".get("cmd_name")) =="mytopbait":
        logger.debug("mytopbait_command triggered")

        post_event("mytopbait_command",event_data.get("event_data", ))
    elif event_data.get("event_data".get("cmd_name")) =="topbait":
        logger.debug("topbait_command triggered")
    
    logger.debug(f"command: {event_data.get("event_data").get("cmd_name")}")

def handle_followage_command(event_data):
    logger.debug("handle_followage_command")
    logger.debug(f'event_data: {event_data}')
    

def handle_snafu_flash_event(event_data):
    logger.debug("Flash event received...")

def handle_stream_online(event_data):
    pass
