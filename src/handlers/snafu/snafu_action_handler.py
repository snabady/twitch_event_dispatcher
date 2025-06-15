import os
from dotenv import load_dotenv
from threading import Thread
from utils.run_command import run_mpv, run_xcowsay
from utils.run_command import GatherTasks


env_file_path = "/home/sna/src/twitch/src/handlers/snafu/.env_snafu_handlers"


def handle_channel_cheer(event: dict ):
    event_data = event.get("event_data")
    print(f"EVENT_DATA: {event_data}")

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
    load_dotenv(env_file_path)
    message = os.getenv("CHEER_TEXT")
    text = text.replace("{user_name}", user_name)
    text = text.replace("{bits}", bits)
    tasks = GatherTasks()

    tasks.add_task(lambda: run_tts(text, os.getenv("VOLUME")))


    
def handle_channel_follow(event: dict):
    event_data = event.get("event_data")
    print(f"EVENT_DATA: {event_data}")
    
    user_id = event_data.get("user_id")
    user_login = event_data.get("user_login")
    user_name = event_data.get("user_name")
    broadcaster_user_id = event_data.get("broadcaster_user_id")
    broadcaster_user_login = event_data.get("broadcaster_user_login")
    broadcaster_user_name = event_data.get("broadcaster_user_name")
    followed_at = event_data.get("followed_at")

    load_dotenv(dotenv_path=env_file_path)
    gather_tasks = GatherTasks()
    
    follow_txt = f'{user_name} {os.getenv("FOLLOW_ALERT_TEXT")}'
    gather_tasks.add_task(lambda: run_xcowsay(os.getenv("SNAAA"), follow_txt, os.getenv("FOLLOW_DISPLAY_TIME"), os.getenv("STREAM_MONITOR") ))

    path_follower_mp3 = os.getenv("ALERTS") + "mp3/new_follower.mp3"
    gather_tasks.add_task(lambda: run_mpv(path_follower_mp3, os.getenv("VOLUME"), no_video=True))

    gather_tasks.run_tasks()    

def hanlde_channel_raid(event: dict):
    event_data = event.get("event_data")
    print(f"EVENT_DATA: {event_data}")
    
    from_broadcaster_user_id = event_data.get("from_broadcaster_user_id")
    from_broadcaster_user_login = event_data.get("from_broadcaster_user_login")
    from_broadcaster_user_name = event_data.get("from_broadcaster_user_name")

    to_broadcaster_user_id = event_data.get("to_broadcaster_user_id")
    to_broadcaster_user_login = event_data.get("to_broadcaster_user_login")
    to_broadcaster_user_name = event_data.get("to_broadcaster_user_name")

    viewers = event_data.get("viewers")

    load_dotenv(dotenv_path=env_file_path)
    raid_text = os.getenv("RAID_TEXT")
    print(raid_text)
    raid_text = raid_text.replace("{broadcaster}", from_broadcaster_user_name)
    raid_text = raid_text.replace("{viewers}", str(viewers))
    #raid_text = "blub"
    tasks = GatherTasks()
    alert_image = os.getenv("ALERTS", "schimpf")+"img/raid.png"
    alert_sound = os.getenv("ALERTS") + "raidsound.webm"

    tasks.add_task(lambda: run_mpv(alert_sound, os.getenv("VOLUME"), True))
    tasks.add_task(lambda: run_xcowsay(alert_image, raid_text, os.getenv("RAID_DISPLAY_TIME"), os.getenv("STREAM_MONITOR")) )
    # TODO
    # !alarm in chat triggern
    # automatischen shoutout
    # OBS!!!! kümmern
    #raid_id = await wst.get_scene_item_id("raid","__raid")
    tasks.run_tasks()
    
    