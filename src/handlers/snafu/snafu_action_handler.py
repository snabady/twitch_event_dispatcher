import datetime 
import requests
import os
import logging
from threading import Thread
from utils.run_command import run_mpv, run_xcowsay, run_tts, create_toilet_file
import asyncio
from utils.run_command import GatherTasks
from utils import log
from events import obsws
from dispatcher.event_dispatcher import post_event, subscribe_event
from utils.file_io import write_file
from handlers import stream_stats , db_handler


logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   

def handle_channel_cheer(event: dict ):
    event_data = event.get("event_data")
    #logger.debug(f"EVENT_DATA: {event_data}")

    is_anonymous = event_data.get("is_anonymous")
    user_id = event_data.get("user_id")
    user_login = event_data.get("user_login")
    user_name = event_data.get("user_name")
    broadcaster_user_id = event_data.get("broadcaster_user_id")
    broadcaster_user_login = event_data.get("broadcaster_user_login")
    broadcaster_user_name = event_data.get("broadcaster_user_name")
    message = event_data.get("message")
    bits = event_data.get("bits")


    if is_anonymous:
        user_name = "anonymous"
    text = os.getenv("CHEER_TEXT")
    text = text.replace("{user_name}", user_name)
    text = text.replace("{bits}",str(bits))
    tasks = GatherTasks()
    tasks.add_task(lambda: run_tts(text))
    tasks.run_tasks()
    msg = f"received channel.cheer from {user_name}: {bits} bits\n"
    event_url="http://localhost:5000/trigger/" + str(bits)
    
    requests.get(event_url) 
def handle_channel_follow(event: dict):
    event_data = event.get("event_data")
    #logger.debug(f"EVENT_DATA: {event_data}")
    
    user_id = event_data.get("user_id")
    user_login = event_data.get("user_login")
    user_name = event_data.get("user_name")
    broadcaster_user_id = event_data.get("broadcaster_user_id")
    broadcaster_user_login = event_data.get("broadcaster_user_login")
    broadcaster_user_name = event_data.get("broadcaster_user_name")
    followed_at = event_data.get("followed_at")

    gather_tasks = GatherTasks()
    msg = f"received channel.follow: ty {user_name}\n"

    query=f"select * from unfollow_events where user_id = {user_id}"
    result = db_handler.execute_query(query, None)
    if result != -1: # refollow!
        irc_text = f"creepy a refollow from {user_name}"
        alert_image = os.getenv("ALERTS", "schimpf")+"img/raid.png"
        gather_tasks.add_task(lambda: run_xcowsay(alert_image, f"{user_name} refollowed..",20, os.getenv("STREAM_MONITOR")) ) 
    else:
        follow_txt = f'{user_name} {os.getenv("FOLLOW_ALERT_TEXT")}'
        gather_tasks.add_task(lambda: run_xcowsay(os.getenv("SNAAA"), follow_txt, os.getenv("FOLLOW_DISPLAY_TIME"), os.getenv("STREAM_MONITOR") ))

        path_follower_mp3 = os.getenv("ALERTS") + "mp3/new_follower.mp3"
        gather_tasks.add_task(lambda: run_mpv(path_follower_mp3, os.getenv("VOLUME"), no_video=True))
        irc_text = f"thank you {user_name} for following x5n4fuPaco"
    
    text = f'{user_name}\njust followed'
    gather_tasks.add_task(lambda: create_toilet_file(os.getenv("TOILET_FOLLOWER_TXT"), "pagga", text))
    post_event("irc_send_message", irc_text)
    gather_tasks.add_task(lambda: post_event("obs_set_source_visibility", {"event_type": "obs_set_source_visibility", "event_data": {"scene_name": "ALERTS", "source_name": "ascii-follower-text", "visible": True}}))

    gather_tasks.run_tasks()    

    # update followerlist
    db_handler.insert_new_follower([user_id, datetime.datetime.now()])

def hanlde_channel_raid(event: dict):
    event_data = event.get("event_data")
    
    from_broadcaster_user_id = event_data.get("from_broadcaster_user_id")
    from_broadcaster_user_login = event_data.get("from_broadcaster_user_login")
    from_broadcaster_user_name = event_data.get("from_broadcaster_user_name")

    to_broadcaster_user_id = event_data.get("to_broadcaster_user_id")
    to_broadcaster_user_login = event_data.get("to_broadcaster_user_login")
    to_broadcaster_user_name = event_data.get("to_broadcaster_user_name")

    viewers = event_data.get("viewers")
    raid_text = os.getenv("RAID_TEXT")
    logger.debug(raid_text)
    raid_text = raid_text.replace("{broadcaster}", from_broadcaster_user_name)
    raid_text = raid_text.replace("{viewers}", str(viewers))
    tasks = GatherTasks()
    alert_image = os.getenv("ALERTS", "schimpf")+"img/raid.png"
    msg = f"received channel.raid from: {from_broadcaster_user_name} with {viewers}\n"    
    irc_msg= f"{from_broadcaster_user_name} fährt das Piratenschiff mit {viewers} Piraten in unseren Hafen x5n4fuPaco"
    post_event("irc_send_message", irc_msg)
    post_event("trigger_wled_preset", 23)
    #tasks.add_task(lambda: obsws.set_source_visibility_wrapper("main_view", "raid", True ))
    tasks.add_task(lambda: post_event("obs_set_source_visibility", {"event_type": "obs_set_source_visibility", "event_data": {"scene_name": "ALERTS", "source_name": "raid_overlay", "visible":True}}))  
    tasks.add_task(lambda: run_xcowsay(alert_image, raid_text, os.getenv("RAID_DISPLAY_TIME"), os.getenv("STREAM_MONITOR")) )
    tasks.add_task(lambda: post_event("obs_set_input_mute", {"event_data":{"audiosource":"desktop_audio", "muted":True}}))
    # TODO raid alert fertig bzw. umbauen, raiders in db und huldigen
    # !alarm in chat triggern
    # automatischen shoutout
    # OBS!!!! kümmern
    #raid_id = await wst.get_scene_item_id("raid","__raid")
    tasks.run_tasks()
    
    
