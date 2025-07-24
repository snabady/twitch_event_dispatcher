import logging 
from utils import log
from utils.run_command import run_xcowsay, run_mpv, run_tts
from utils.run_command import GatherTasks
from utils.file_io import write_file
logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   
import os
from dotenv import load_dotenv 
env_file_path = "/home/sna/src/twitch/src/handlers/snafu/.env_snafu_handlers"

load_dotenv(env_file_path)
    

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
    logger.debug ("yes we did it \n################################################################################")
    gather_task = GatherTasks()
    msg = f"{user_name} vielen dank. fuer deinen Geschenksub"
    write_file("/home/sna/5n4fu_stream/data/sna_event.txt", "a", msg)
    gather_task.add_task(lambda: run_tts(msg))
    msg = f'{user_name} just gifted a sub to...! Danke !'
    gather_task.add_task(lambda: run_xcowsay(os.getenv("SNAAA"), msg, 20, 1, False))     
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
    logger.debug ("yes we did it \n################################################################################")

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
    logger.debug ("yes we did it \n################################################################################")
    gather_task = GatherTasks()
    msg = f"{user_name} "
    write_file("/home/sna/5n4fu_stream/data/sna_event.txt", "a", msg)
    gather_task.add_task(lambda: run_tts(msg))
    msg = f'{user_name} hat gerade ein nen Sub verschenkt!'
    gather_task.add_task(lambda: run_xcowsay(os.getenv("SNAAA"), msg, 20, 1, False))     
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
    write_file("/home/sna/5n4fu_stream/data/sna_event.txt", "a", msg)
    gather_task.add_task(lambda: run_xcowsay(os.getenv("SNAAA") ,msg, 20, 1, False))     
    msg = f"{user_name} vielen dank. fuer deinen sab"
    gather_task.add_task(lambda: run_tts(msg))
    gather_task.run_tasks()
    #cumulative_months = event_data["cumulative_months"]
    #duration_months = event_data["duration_months"]
    logger.debug ("yes we did it \n################################################################################")
