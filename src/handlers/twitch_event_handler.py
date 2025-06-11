
from dispatcher.event_dispatcher import subscribe_event

from handlers import snafu_subscribe_handler






def handle_twitch_subscribe_event(event):
    
    subscribe_events = {    "channel.subscribe": snafu_subscribe_handler.handle_channel_subscribe, 
                            "channel.subscription.end":  snafu_subscribe_handler.handle_subscription_end , 
                            "channel.subscription.gift":  snafu_subscribe_handler.channel_subscription_grift, 
                            "channel.subscription.message":  snafu_subscribe_handler.channel_subscription_message 
                        }


    event_data = event.get("event_data")
    event_type = event.get("event_type")
    event_map = event.get("event_map")
    fn = subscribe_events.get(event_type)
    fn(event)

def handle_twitch_streaminfo_event(event):
    streaminfo_events = { 

    }
    raise NotImplementedError

def handle_twitch_charity_event(event):
    charity_events = {}
    raise NotImplementedError

def handle_twitch_action_event(event):
    raise NotImplementedError

def hanle_twitch_moderate_event(event):
    raise NotImplementedError

def handle_twitch_ban_event(event):
    raise NotImplementedError

def handle_twitch_goal_event(event):
    
    raise NotImplementedError
def handle_twitch_channelpint_event(event):
    
    raise NotImplementedError
def handle_twitch_ban_event(event):
    
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



