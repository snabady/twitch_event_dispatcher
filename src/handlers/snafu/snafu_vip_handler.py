import logging
from src.utils import log
from src.handlers import db_handler
from datetime import datetime
from src.dispatcher.event_dispatcher import post_event
logger = logging.getLogger("VIP handler")
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   



def handle_vip_add(event: dict):
    event_data = event.get("event_data")
    logger.debug(event_data)
    values = [event_data.get("user_id") , 
              1, 
              event_data.get("user_name"), 
              event_data.get("user_login"), 
              datetime.now()
              ]
    db_handler.update_special_users(values ,is_vip=1)
    post_event("trigger_get_vipsis", None)
    post_event("update_current_vips", None)

    # -> send alert to greet new vip xD
    # -> create e-paper-VIP-badge
    post_event("create_vip_badge", event_data)

def handle_vip_remove(event: dict):
    event_data = event.get("event_data")
    logger.debug(event_data)
    values =[event_data.get("user_id"), 
             0, 
             event_data.get("user_name"),
             event_data.get("user_login"), 
             datetime.now()
             ]
    db_handler.update_special_users(values,is_vip=0)
    post_event("trigger_get_vipsis", None)
    post_event("update_current_vips", None)
    # clear e-paper-VIP-badge
