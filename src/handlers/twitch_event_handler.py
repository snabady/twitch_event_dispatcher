
from dispatcher.event_dispatcher import subscribe_event








def handle_twitch_subscribe_event(event):
    
    print(f" TWITCH HANDLER: received twitch subscribe event: ")
    
    
    
    subscribe_events = {    "channel.subscribe": handle_channel_subscribe, 
                            "channel.subscription.end": handle_subscription_end , 
                            "channel.subscription.gift": channel_subscription_grift, 
                            "channel.subscription.message": channel_subscription_message }


    event_data = event.get("event_data")
    event_type = event.get("event_type")
    event_map = event.get("event_map")
    fn = subscribe_events.get(event_type)
    fn(event)

def handle_twitch_streaminfo_event(event):
    raise NotImplementedError

def handle_twitch_charity_event(event):
    raise NotImplementedError

def handle_twitch_action_event(event):
    raise NotImplementedError

def hanle_twitch_moderate_event(event):
    raise NotImplementedError

def handle_twitch_ban_event(event):
    raise NotImplementedError

def handle_twitch_goal_event(event):
    print(f" TWITCH HANDLER: received twitch_goal_event: ")
    raise NotImplementedError
def handle_twitch_channelpint_event(event):
    print(f" TWITCH HANDLER: received twitch_channelpoint_event: ")
    raise NotImplementedError
def handle_twitch_ban_event(event):
    print(f" TWITCH HANDLER: received twitch_ban_event: ")
    raise NotImplementedError

def handle_twitch_poll_event(event):
    raise NotImplementedError

def handle_twitch_prediction_event(event):
    raise NotImplementedError

def handle_twitch_hypetrain_event(event):
    raise NotImplementedError


def handle_twitch_shoutout_event(event):
    raise NotImplementedError


def handle_twitch_streaminfo_event(event):
    raise NotImplementedError

def handle_twitch_moderate_event(event):
    raise NotImplementedError

def handle_channel_subscribe(event):
    print ("handle_channel_subscribe")
    


    event_data = event.get("event_data")
    
    user_id = event_data["user_id"] 
    user_login = event_data["user_login"]
    user_name = event_data["user_name"]
    broadcaster_user_id = event_data["broadcaster_user_id"]
    broadcaster_user_login = event_data["broadcaster_user_login"]
    broadcaster_user_name = event_data["broadcaster_user_name"]
    tier = event_data["tier"]
    is_gift = event_data["is_gift"]



def handle_subscription_end():
    raise NotImplementedError

def channel_subscription_grift():
    raise NotImplementedError




def channel_subscription_message():
    raise NotImplementedError