#import event_dispatcher as blub
#from dispatcher.event_dispatcher import subscribe_event
from dispatcher.event_dispatcher import subscribe_event
def handle_twitch_subscribe_event(data: str):
    
    print(f"received twitch subscribe event: {data}")

subscribe_event("twitch_subscribe_event", handle_twitch_subscribe_event)