
from dispatcher.event_dispatcher import subscribe_event

from handlers import snafu_subscribe_handler

def handle_twitch_subscribe_event(event):
    
    subscribe_events = {    
        "channel.subscribe": snafu_subscribe_handler.handle_channel_subscribe, 
        "channel.subscription.end":  snafu_subscribe_handler.handle_subscription_end , 
        "channel.subscription.gift":  snafu_subscribe_handler.channel_subscription_grift, 
        "channel.subscription.message":  snafu_subscribe_handler.channel_subscription_message 
}

    event_type = event.get("event_type")
    fn = subscribe_events.get(event_type)
    fn(event)

def handle_twitch_streaminfo_event(event):
    streaminfo_events = { 
        "listen.stream.online": snafu_streaminfo_handler.handle_stream_online,
        "listen.stream.offline":  snafu_streaminfo_handler.handle_stream_online,
        "listen.channel.update_v2":  snafu_streaminfo_handler.handle_channel_update_v2,
        "listen.channel.update":  snafu_streaminfo_handler.hanlde_channel_update
    }

    event_type = event.get("event_type")
    fn = subscribe_events.get(event_type)
    fn(event)

def handle_twitch_charity_event(event):
    charity_events = {
        "channel.charity_campaign.donate": None,
        "channel.charity_campaign.progress": None,
        "channel.charity_campaign.start ": None,
        "channel.charity_campaign.stop": None, 
    }

    raise NotImplementedError

def handle_twitch_action_event(event):
    action_events = {
        "channel.cheer": None,
        "channel.follow": None,
        "channel.raid": None,
    }
    raise NotImplementedError

def hanle_twitch_moderate_event(event):
    moderate_event = {
        "channel.moderator.add": None,
        "channel.moderator.remove": None,
        "channel.ad_break.begin ": None
    }
    raise NotImplementedError

def handle_twitch_ban_event(event):
    ban_events = {
        "channel.ban" : None,
        "channel.unban" : None, 
        "channel.unban_request.create": None,
        "channel.unban_request.resolve": None
    }
    raise NotImplementedError

def handle_twitch_goal_event(event):
    goal_events = {
        "channel.goal.begin": None, 
        "channel.goal.end" : None,
        "channel.goal.progress": None
    }
    raise NotImplementedError

def handle_twitch_channelpoint_event(event):
    channelpoint_events ={
        "channel.channel_points_custom_reward.add" : None,
        "channel.channel_points_custom_reward.remove" : None,
        "channel.channel_points_custom_reward.update" :  None,
        "channel.channel_points_custom_reward_redemption.add" : None,
        "channel.channel_points_custom_reward_redemption.update" : None
    }
    raise NotImplementedError

def handle_twitch_poll_event(event):
    poll_events = {
        "channel.poll.begin" : None, 
        "channel.poll.end" : None, 
        "channel.poll.progress": None
    }
    raise NotImplementedError

def handle_twitch_prediction_event(event):
    prediction_events = {
        "channel.prediction.begin": None,
        "channel.prediction.end": None,
        "channel.prediction.lock": None,
        "channel.prediction.progress": None
    }
    raise NotImplementedError

def handle_twitch_hypetrain_event(event):
    hypetrain_events = {
        "channel.hype_train.begin" : None, 
        "channel.hype_train.end" : None,
        "channel.hype_train.progress":None
    }
    raise NotImplementedError

def handle_twitch_shoutout_event(event):
    shoutout_events= {
        "channel.shoutout.create": None, 
        "channel.shoutout.receive": None
    }
    raise NotImplementedError





