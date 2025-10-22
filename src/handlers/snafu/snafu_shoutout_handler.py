from dispatcher.event_dispatcher import post_event

def handle_shoutout_create(event):
    print("SHOUTOUT CREATE ")
    event_data = event.get("event_data")
    print(event_data)
    msg = f" shoutout to: {event_data.get("to_broadcaster_user_name")}! consider following! next possible shoutout:  {event_data.get("target_cooldown_ends_at")} "
    print (msg)
    post_event("irc_send_message", msg)

def handle_shoutout_receive(event):
    print("SHOUTOUT RECEIVE ")
    print(event.get("event_data"))
    event_data = event.get("event_data")
    msg = f"{event_data.get("from_broadcaster_user_name")} gave us a shoutout {event_data.get("viewer_count")} viewers seen this. Checkout {event_data.get("from_broadcaster_user_name")} ens seems to be nice!"
    print(msg)
    post_event("irc_send_message", msg)
