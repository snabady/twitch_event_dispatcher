



def handle_custom_reward_add (event: dict):
    print("---------------->")
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
    print ("WE DID IT")

def handle_reward_remove (event: dict):
    event_data = event.get("event_data")
    print(f"EVENT_DATA:{event_data}")
    
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
"""
{'id': '26738b30-8a96-dcba-538e-07959b80f8df', 'broadcaster_user_id': '42226127', 'broadcaster_user_login'
: 'testBroadcaster', 'broadcaster_user_name': 'testBroadcaster', 'is_enabled': True, 'is_paused': False, 'is_in_stock
': True, 'title': 'Test Reward from CLI', 'cost': 150, 'prompt': 'Redeem Your Test Reward from CLI', 'is_user_input_r
equired': True, 'should_redemptions_skip_request_queue': False, 'max_per_stream': {'is_enabled': True, 'value': 100},
 'max_per_user_per_stream': {'is_enabled': True, 'value': 100}, 'background_color': '#c0ffee', 'image': {'url_1x': 'h
ttps://static-cdn.jtvnw.net/image-1.png', 'url_2x': 'https://static-cdn.jtvnw.net/image-2.png', 'url_4x': 'https://st
atic-cdn.jtvnw.net/image-4.png'}, 'default_image': {'url_1x': 'https://static-cdn.jtvnw.net/default-1.png', 'url_2x':
 'https://static-cdn.jtvnw.net/default-2.png', 'url_4x': 'https://static-cdn.jtvnw.net/default-4.png'}, 'global_coold
own': {'is_enabled': True, 'seconds': 300}, 'cooldown_expires_at': '2025-06-12T04:52:42.115952+00:00', 'redemptions_r
edeemed_current_stream': 0}
"""


def handle_reward_update (event: dict):

    event_data = event.get("event_data")
    print(f"EVENT_DATA:{ event_data}")
    
def handle_reward_redemption_add (event: dict):
    event_data = event.get("event_data")
    print(f"EVENT_DATA:{ event_data}")
    
def handle_redemption_update(event: dict):
    event_data = event.get("event_data")
    print(f"EVENT_DATA:{ event_data}")

# v1 // v2
def handle_automatic_reward_redemption_add(event: dict):
    pass