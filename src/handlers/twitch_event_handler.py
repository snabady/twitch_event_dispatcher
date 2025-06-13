
from dispatcher.event_dispatcher import subscribe_event

from handlers.snafu import snafu_subscribe_handler, snafu_streaminfo_handler,snafu_charity_handler, snafu_action_handler, snafu_moderate_handler, snafu_ban_handler, snafu_goal_handler, snafu_channelpoint_handler, snafu_poll_handler, snafu_prediction_handler, snafu_hypetrain_handler, snafu_shoutout_handler


def handle_twitch_subscribe_event(event):
    
    subscribe_events = {    
        "channel.subscribe":                snafu_subscribe_handler.handle_channel_subscribe, 
        "channel.subscription.end":         snafu_subscribe_handler.handle_subscription_end , 
        "channel.subscription.gift":        snafu_subscribe_handler.channel_subscription_grift, 
        "channel.subscription.message":     snafu_subscribe_handler.channel_subscription_message 
}

    event_type = event.get("event_type")
    fn = subscribe_events.get(event_type)
    fn(event)

def handle_twitch_streaminfo_event(event):
    streaminfo_events = { 
        "stream.online":         snafu_streaminfo_handler.handle_stream_online,
        "stream.offline":        snafu_streaminfo_handler.handle_stream_offline,
        "channel.update_v2":     snafu_streaminfo_handler.handle_channel_update_v2,
        "channel.update":        snafu_streaminfo_handler.hanlde_channel_update
    }

    event_type = event.get("event_type")
    fn = streaminfo_events.get(event_type)
    fn(event)

def handle_twitch_charity_event(event):
    charity_events = {
        "channel.charity_campaign.donate":      snafu_charity_handler.handle_charity_campaign_donate,
        "channel.charity_campaign.progress":    snafu_charity_handler.handle_campaign_progress,
        "channel.charity_campaign.start ":      snafu_charity_handler.handle_charity_campaign.start,
        "channel.charity_campaign.stop":        snafu_charity_handler.handle_charity_campaign.stop 
    }
    event_type = event.get("event_type")
    fn = streaminfo_events.get(event_type)
    fn(event)
    

def handle_twitch_action_event(event):
    action_events = {
        "channel.cheer":    snafu_action_handler.handle_channel_cheer,
        "channel.follow":   snafu_action_handler.handle_channel_follow,
        "channel.raid":     snafu_action_handler.hanlde_channel_raid
    }
    event_type = event.get("event_type")
    fn = action_events.get(event_type)
    fn(event)

def hanle_twitch_moderate_event(event):
    moderate_event = {
        "channel.moderator.add": snafu_moderate_handler.handle_moderator_add,
        "channel.moderator.remove": snafu_moderate_handler.handle_moderator_remove,
        "channel.ad_break.begin ": snafu_moderate_handler.handle_ad_break_begin
    }
    event_type = event.get("event_type")
    fn = streaminfo_events.get(event_type)
    fn(event)

def handle_twitch_ban_event(event):
    ban_events = {
        "channel.ban" :                     snafu_ban_handler.handle_channel_ban,
        "channel.unban" :                   snafu_ban_handler.channel_unban, 
        "channel.unban_request.create":     snafu_ban_handler.channel_unban_request_create,
        "channel.unban_request.resolve":    snafu_ban_handler.unban_request_resolve
    }
    event_type = event.get("event_type")
    fn = streaminfo_events.get(event_type)
    fn(event)

def handle_twitch_goal_event(event):
    goal_events = {
        "channel.goal.begin": snafu_goal_handler.handle_goal_begin, 
        "channel.goal.end" : snafu_goal_handler.handle_goal_end,
        "channel.goal.progress": snafu_goal_handler.handle_goal_progress
    }
    event_type = event.get("event_type")
    fn = goal_events.get(event_type)
    fn(event)

def handle_twitch_channelpoint_event(event):
    channelpoint_events ={
        "channel.channel_points_custom_reward.add" : snafu_channelpoint_handler.handle_custom_reward_add,
        "channel.channel_points_custom_reward.remove" : snafu_channelpoint_handler.handle_reward_remove,
        "channel.channel_points_custom_reward.update" :  snafu_channelpoint_handler.handle_reward_update,
        "channel.channel_points_custom_reward_redemption.add" : snafu_channelpoint_handler.handle_reward_redemption_add,
        "channel.channel_points_custom_reward_redemption.update" : snafu_channelpoint_handler.handle_redemption_update,
        "channel.channel_points_automatic_reward_redemption.add" : snafu_channelpoint_handler.handle_automatic_reward_redemption_add
    }
    event_type = event.get("event_type")
    fn = channelpoint_events.get(event_type)
    fn(event)

def handle_twitch_poll_event(event):
    poll_events = {
        "channel.poll.begin" : snafu_poll_handler.handle_poll_begin, 
        "channel.poll.end" : snafu_poll_handler.handle_poll_end, 
        "channel.poll.progress": snafu_poll_handler.handle_poll_progress
    }
    event_type = event.get("event_type")
    fn = poll_events.get(event_type)
    fn(event)

def handle_twitch_prediction_event(event):
    prediction_events = {
        "channel.prediction.begin": snafu_prediction_handler.handle_prediction_begin,
        "channel.prediction.end": snafu_prediction_handler.handle_prediction_end,
        "channel.prediction.lock": snafu_prediction_handler.handle_prediction_lock,
        "channel.prediction.progress": snafu_prediction_handler.handle_prediction_progress
    }
    event_type = event.get("event_type")
    fn = streaminfo_events.get(event_type)
    fn(event)

def handle_twitch_hypetrain_event(event):
    hypetrain_events = {
        "channel.hype_train.begin" : snafu_hypetrain_handler.handle_hypetrain_begin, 
        "channel.hype_train.end" : snafu_hypetrain_handler.handle_hypetrain_end,
        "channel.hype_train.progress":snafu_hypetrain_handler.handle_hypetrain_end
    }
    event_type = event.get("event_type")
    fn = hypetrain_events.get(event_type)
    fn(event)

def handle_twitch_shoutout_event(event):
    shoutout_events= {
        "channel.shoutout.create": snafu_shoutout_handler.handle_shoutout_create, 
        "channel.shoutout.receive": snafu_shoutout_handler.handle_shoutout_receive
    }
    event_type = event.get("event_type")
    fn = streaminfo_events.get(event_type)
    fn(event)





