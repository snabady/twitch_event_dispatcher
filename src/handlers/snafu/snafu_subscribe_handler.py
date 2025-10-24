import logging 
from utils import log
from utils.run_command import run_xcowsay, run_mpv, run_tts
from utils.run_command import GatherTasks
from utils.file_io import write_file
logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   
import os

def handle_channel_subscribe(event):
    logger.debug ("handle_channel_subscribe")

    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")
    user_id = event_data["user_id"] 
    user_login = event_data["user_login"]
    user_name = event_data["user_name"]
    broadcaster_user_id = event_data["broadcaster_user_id"]
    broadcaster_user_login = event_data["broadcaster_user_login"]
    broadcaster_user_name = event_data["broadcaster_user_name"]
    tier = event_data["tier"]
    is_gift = event_data["is_gift"]
    gather_task = GatherTasks()
    logger.debug(f"is_gift: {is_gift}")
    if is_gift:
        msg = f"{user_name} hat nen sub geschenkt bekommen! welcome!"
    else:
        msg = f'{user_name} danke fuer deinen sub!'
    gather_task.add_task(lambda: run_xcowsay(os.getenv("SNAAA"), msg, 20, 0, False))     
    gather_task.add_task(lambda: run_tts(msg))
    gather_task.run_tasks()
    #cumulative_months = event_data["cumulative_months"]
    #duration_months = event_data["duration_months"]

def handle_subscription_end(event):

    created_at = event.get("timestamp_created")
    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")
    user_id = event_data["user_id"] 
    user_login = event_data["user_login"]
    user_name = event_data["user_name"]
    broadcaster_user_id = event_data["broadcaster_user_id"]
    broadcaster_user_login = event_data["broadcaster_user_login"]
    broadcaster_user_name = event_data["broadcaster_user_name"]
    tier = event_data["tier"]
    is_gift = event_data["is_gift"]

def channel_subscription_grift(event):
    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")
    user_id = event_data["user_id"] 
    user_login = event_data["user_login"]
    user_name = event_data["user_name"]
    broadcaster_user_id = event_data["broadcaster_user_id"]
    broadcaster_user_login = event_data["broadcaster_user_login"]
    broadcaster_user_name = event_data["broadcaster_user_name"]
    tier = event_data["tier"]
    
    
    #cumulative_total = event_data["cumulative_total"]
    total = event_data["total"]
    gather_task = GatherTasks()
    msg = f"{user_name} "
    gather_task.add_task(lambda: run_tts(msg))
    msg = f'{user_name} hat gerade {total} sub(s) verschenkt!'
    gather_task.add_task(lambda: run_xcowsay(os.getenv("SNAAA"), msg, 20, 0, False))     
    gather_task.run_tasks()
    #cumulative_months = event_data["cumulative_months"]
    #duration_months = event_data["duration_months"]

def channel_subscription_message(event):
    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")
    user_id = event_data["user_id"] 
    user_login = event_data["user_login"]
    user_name = event_data["user_name"]
    broadcaster_user_id = event_data["broadcaster_user_id"]
    broadcaster_user_login = event_data["broadcaster_user_login"]
    broadcaster_user_name = event_data["broadcaster_user_name"]
    tier = event_data["tier"]


    message = event_data["message"] # string including emotes e.g.
    #{'text': 'Hello from the Twitch CLI! twitchdevLeek', 'emotes': [{'begin': 26, 'end': 39, 'id': '304456816'}]}
    gather_task = GatherTasks()
    msg = f'{user_name} hat gesubbt ! Danke!'
    gather_task.add_task(lambda: run_xcowsay(os.getenv("SNAAA") ,msg, 20, 0, False))     
    msg = f"{user_name} danke fuer deinen sub"
    gather_task.add_task(lambda: run_tts(msg))
    gather_task.run_tasks()
    #cumulative_months = event_data["cumulative_months"]
    #duration_months = event_data["duration_months"]
