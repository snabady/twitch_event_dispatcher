import logging
from utils import log


logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)  

def handle_stream_online(event: dict):
    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")
    id_                     = event.get("id")
    broadcaster_user_id     = event.get("broadcaster_user_id")
    broadcaster_user_login  = event.get("broadcaster_user_login")
    broadcaster_user_name   = event.get("broadcaster_user_name")
    type_                   = event.get("type")
    started_at              = event.get("started_at")
    
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

    logger.debug("WE DID IT ")