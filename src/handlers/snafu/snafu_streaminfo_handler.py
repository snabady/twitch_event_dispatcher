import datetime 
import logging
from src.utils import log
from src.events import obsws
from src.handlers.twitchapi import trigger_follower_count, trigger_sub_count
from src.dispatcher.event_dispatcher import post_event
import os
#from handlers.twitchapi import myTwitch
from src.utils.file_io import write_file

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)
#tapi = twitchapi.myTwitch()  

def handle_stream_online(event: dict):
    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")
    id_                     = event.get("id")
    broadcaster_user_id     = event.get("broadcaster_user_id")
    broadcaster_user_login  = event.get("broadcaster_user_login")
    broadcaster_user_name   = event.get("broadcaster_user_name")
    type_                   = event.get("type")
    started_at              = event.get("started_at")
    # obs:
    trigger_follower_count()
    trigger_sub_count()
    
    # fishies!
    # TODO
    # asciiquarium
    # as long as intro-music -> obs-scene activate ascii
    # check the write overlay
    logger.info("Stream just went ONLINE... setting up things")
    obsws.trigger_hotkey_by_name_wrapper("timer_start_hotkey")
    post_event("set_stream_online", {"event_type": "set_stream_online", "event_data": True})
    obsws.stream_online = True
    post_event("stream_online_event", event_data)
    msg = f"5n4fu is now live!  {datetime.datetime.now()} "
    post_event("irc_send_message", msg)

def handle_stream_offline(event: dict):
    """
    event_data: {'broadcaster_user_id': '42226127',
     'broadcaster_user_login': 'testBroadcaster',
      'broadcaster_user_name': 'testBroadcaster'}
    """
    event_data = event.get("event_data")
    
    logger.debug(f"event_data: {event_data}")
    broadcaster_user_id = event.get("broadcaster_user_id")
    broadcaster_user_login = event.get("broadcaster_user_login")
    broadcaster_user_name = event.get("broadcaster_user_name")

#    obsws.trigger_hotkey_by_name_wrapper("timer_stop_hotkey")
    # stats schreiben
    post_event("set_stream_online", {"event_type": "set_stream_online", "event_data": False})
    logger.debug("WE DID IT ")
    post_event("stream_offline_event", event_data)    
    post_event("stream_online_event", False)
    msg = "5n4fu is now offline. so long and thanks for all the fish.."
    post_event("irc_send_message", msg)
def handle_channel_update_v2(event: dict):
    """
    event_data: {'broadcaster_user_id': '42226127', 
                'broadcaster_user_login': 'testBroadcaster', 
                'broadcaster_user_name': 'testBroadcaster', 
                'title': 'Example title from the CLI!', 
                'language': 'en', 
                'category_id': '5462', 
                'category_name': 'Just Chatting', 
                'content_classification_labels': ['MatureGame', 'ViolentGraphic']}

    """
    
    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")
    broadcaster_user_id             = event_data("broadcaster_user_id")
    broadcaster_user_login          = event_data("broadcaster_user_login")
    broadcaster_user_name           = event_data("broadcaster_user_name")
    title                           = event_data("title")
    language                        = event_data("language")
    category_id                     = event_data("category_id")
    category_name                   = event_data("category_name")
    content_classification_labels   = event_data("content_classification_labels")
    # starting-scene
    # playlist start
    # refresh fishis
    # check values -> overlay bottom

    msg =f"streamtitle is now: {event_data.get("title")}"
    post_event("irc_send_message", msg)
    logger.debug("WE DID IT ")
    
def hanlde_channel_update(event: dict):
    """
    event_data: {'broadcaster_user_id': '42226127', 
                'broadcaster_user_login': 'testBroadcaster',
                'broadcaster_user_name': 'testBroadcaster', 
                'title': 'Example title from the CLI!', 
                'language': 'en', 
                'category_id': '4164', 
                'category_name': 'Just Chatting'}
    """
    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")
    #obsws.switch_scene_wrapper("logview")
    
    msg =f"streamtitle changed to: {event_data.get("title")}"
    post_event("irc_send_message", msg)
    
