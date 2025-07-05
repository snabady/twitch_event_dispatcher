import logging 
from utils import log

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   


def handle_custom_reward_add (event: dict):
    logger.debug("---------------->")
    event_data = event.get("event_data")
    
    event_id    = event_data.get("id")
    broadcaster_user_id             = event_data.get("broadcaster_user_id")
    broadcaster_user_login          = event_data.get("broadcaster_user_login")
    broadcaster_user_name           = event_data.get("broadcaster_user_name")
    is_enabled                      = event_data.get("is_enabled")
    is_paused                       = event_data.get("is_paused")
    is_in_stock                     = event_data.get("is_in_stock")
    title                           = event_data.get("title")
    cost                            = event_data.get("cost")
    prompt                          = event_data.get("prompt")
    is_user_input_required          = event_data.get("is_user_input_required")
    should_redemptions_skip_request_queue = event_data.get("should_redemptions_skip_request_queue")
    max_per_stream                  = event_data.get("max_per_stream") # 'max_per_stream': {'is_enabled': True, 'value': 100}
    max_per_user_per_stream         = event_data.get("max_per_user_per_stream") #{'is_enabled': True, 'value': 100}
    background_color                = event_data.get("background_color")
    image                           = event_data.get("image")# {'url_1x': 'https://static-cdn.jtvnw.net/image-1.png', 'url_2x': 'https://static-cdn.jtvnw.net/image-2.png', 'url_4x': 'https://static-cdn.jtvnw.net/image-4.png'}
    default_image                   = event_data.get("default_image")
    global_cooldown                 = event_data.get("global_cooldown")#{'is_enabled': True, 'seconds': 300}
    cooldown_expires_at             = event_data.get("cooldown_expire")
    redemptions_redeemed_current_stream = event_data.get("redemptions_redeemed_current_stream")
    logger.debug ("WE DID IT")

def handle_reward_remove (event: dict):
    event_data = event.get("event_data")
    logger.debug(f"EVENT_DATA:{event_data}")
    
    event_id    = event_data.get("id")
    broadcaster_user_id             = event_data.get("broadcaster_user_id")
    broadcaster_user_login          = event_data.get("broadcaster_user_login")
    broadcaster_user_name           = event_data.get("broadcaster_user_name")
    is_enabled                      = event_data.get("is_enabled")
    is_paused                       = event_data.get("is_paused")
    is_in_stock                     = event_data.get("is_in_stock")
    title                           = event_data.get("title")
    cost                            = event_data.get("cost")
    prompt                          = event_data.get("prompt")
    is_user_input_required          = event_data.get("is_user_input_required")
    should_redemptions_skip_request_queue = event_data.get("should_redemptions_skip_request_queue")
    max_per_stream                  = event_data.get("max_per_stream") # 'max_per_stream': {'is_enabled': True, 'value': 100}
    max_per_user_per_stream         = event_data.get("max_per_user_per_stream") #{'is_enabled': True, 'value': 100}
    background_color                = event_data.get("background_color")
    image                           = event_data.get("image")# {'url_1x': 'https://static-cdn.jtvnw.net/image-1.png', 'url_2x': 'https://static-cdn.jtvnw.net/image-2.png', 'url_4x': 'https://static-cdn.jtvnw.net/image-4.png'}
    default_image                   = event_data.get("default_image")
    global_cooldown                 = event_data.get("global_cooldown")#{'is_enabled': True, 'seconds': 300}
    cooldown_expires_at             = event_data.get("cooldown_expire")
    redemptions_redeemed_current_stream = event_data.get("redemptions_redeemed_current_stream")



def handle_reward_update (event: dict):

    event_data = event.get("event_data")
    logger.debug(f"EVENT_DATA:{ event_data}")
    
def handle_reward_redemption_add (event: dict):
    event_data = event.get("event_data")
    logger.debug(f"EVENT_DATA:{ event_data}")
    
def handle_redemption_update(event: dict):
    event_data = event.get("event_data")
    logger.debug(f"EVENT_DATA:{ event_data}")

# v1 // v2
def handle_automatic_reward_redemption_add(event: dict):
    pass