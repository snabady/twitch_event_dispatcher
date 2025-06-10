
from dispatcher.event_dispatcher import subscribe_event
def handle_twitch_subscribe_event(event):
    
    print(f" TWITCH HANDLER: received twitch subscribe event: ")
    #event_keys = event.keys()
    
    event_data = event.get("event_data")
    event_type = event.get("event_type")
    event_map = event.get("event_map")



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