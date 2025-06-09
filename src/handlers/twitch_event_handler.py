from event_dispatcher import subscribe_event





def handle_twitch_subscribe_event(data: str):
    
    print(f"received twitch subscribe event: {data}")




subscribe_event("twitch_subscribe_event", handle_twitch_subscribe_event)