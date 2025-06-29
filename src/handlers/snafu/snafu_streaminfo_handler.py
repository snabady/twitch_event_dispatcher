import logging
from utils import log
from events import obsws
#from handlers import twitchapi
from handlers import twitchapi


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
    
    # check followercount
    #tapi.trigger_follower_count()
    # check subportercount
    # fishies!
    
    logger.info("Stream just went ONLINE... setting up things")
    obsws.trigger_hotkey_by_name_wrapper("timer_start_hotkey")
    logger.debug("WE DID IT ")


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

    obsws.trigger_hotkey_by_name_wrapper("timer_stop_hotkey")
    # stats schreiben

    logger.debug("WE DID IT ")

    
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
    logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")

    #obsws.set_source_visibility_wrapper("main_view", "raid", True)
    obsws.switch_scene_wrapper("logview")
    logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")