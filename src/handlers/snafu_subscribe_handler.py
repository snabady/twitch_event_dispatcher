def handle_channel_subscribe(event):
    print ("handle_channel_subscribe")

    event_data = event.get("event_data")
    print(f"event_data: {event_data}")
    user_id = event_data["user_id"] 
    user_login = event_data["user_login"]
    user_name = event_data["user_name"]
    broadcaster_user_id = event_data["broadcaster_user_id"]
    broadcaster_user_login = event_data["broadcaster_user_login"]
    broadcaster_user_name = event_data["broadcaster_user_name"]
    tier = event_data["tier"]
    is_gift = event_data["is_gift"]
    print ("yes we did it \n################################################################################")

def handle_subscription_end(event):

    created_at = event.get("timestamp_created")
    event_data = event.get("event_data")
    print(f"event_data: {event_data}")
    user_id = event_data["user_id"] 
    user_login = event_data["user_login"]
    user_name = event_data["user_name"]
    broadcaster_user_id = event_data["broadcaster_user_id"]
    broadcaster_user_login = event_data["broadcaster_user_login"]
    broadcaster_user_name = event_data["broadcaster_user_name"]
    tier = event_data["tier"]
    is_gift = event_data["is_gift"]
    print ("yes we did it \n################################################################################")

def channel_subscription_grift(event):
    event_data = event.get("event_data")
    print(f"event_data: {event_data}")
    user_id = event_data["user_id"] 
    user_login = event_data["user_login"]
    user_name = event_data["user_name"]
    broadcaster_user_id = event_data["broadcaster_user_id"]
    broadcaster_user_login = event_data["broadcaster_user_login"]
    broadcaster_user_name = event_data["broadcaster_user_name"]
    tier = event_data["tier"]
    
    
    cumulative_total = event_data["cumulative_total"]
    total = event_data["total"]
    print ("yes we did it \n################################################################################")



def channel_subscription_message(event):
    event_data = event.get("event_data")
    print(f"event_data: {event_data}")
    user_id = event_data["user_id"] 
    user_login = event_data["user_login"]
    user_name = event_data["user_name"]
    broadcaster_user_id = event_data["broadcaster_user_id"]
    broadcaster_user_login = event_data["broadcaster_user_login"]
    broadcaster_user_name = event_data["broadcaster_user_name"]
    tier = event_data["tier"]


    message = event_data["message"] # string including emotes e.g.
    #{'text': 'Hello from the Twitch CLI! twitchdevLeek', 'emotes': [{'begin': 26, 'end': 39, 'id': '304456816'}]}
    
    cumulative_months = event_data["cumulative_months"]
    duration_months = event_data["duration_months"]
    print ("yes we did it \n################################################################################")