import os
import logging 
from utils import log
import random
from handlers.db_handler import get_active_channelpoint_rewards
from dispatcher.event_dispatcher import post_event
from utils.run_command import run_mpv
from utils import run_command
from utils.file_io import write_file, write_snaalert_file
logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   
#https://www.twitch.tv/popout/5n4fu/reward-queue

def handle_custom_reward_add (event: dict):
    logger.debug("---------------->")
    event_data = event.get("event_data")
    
    event_id    = event_data.get("id")
    broadcaster_user_id             = event_data.get("broadcaster_user_id")
    broadcaster_user_login          = event_data.get("broadcaster_user_login")
    broadcaster_user_name           = event_data.get("broadcaster_user_name")
    is_enabled                      = event_data.get("is_enabled")
    is_paused                       = event_data.get("is_paused")
    is_in_stock                     = event_data.get("is_in_stock")
    title                           = event_data.get("title")
    cost                            = event_data.get("cost")
    prompt                          = event_data.get("prompt")
    is_user_input_required          = event_data.get("is_user_input_required")
    should_redemptions_skip_request_queue = event_data.get("should_redemptions_skip_request_queue")
    max_per_stream                  = event_data.get("max_per_stream") # 'max_per_stream': {'is_enabled': True, 'value': 100}
    max_per_user_per_stream         = event_data.get("max_per_user_per_stream") #{'is_enabled': True, 'value': 100}
    background_color                = event_data.get("background_color")
    image                           = event_data.get("image")# {'url_1x': 'https://static-cdn.jtvnw.net/image-1.png', 'url_2x': 'https://static-cdn.jtvnw.net/image-2.png', 'url_4x': 'https://static-cdn.jtvnw.net/image-4.png'}
    default_image                   = event_data.get("default_image")
    global_cooldown                 = event_data.get("global_cooldown")#{'is_enabled': True, 'seconds': 300}
    cooldown_expires_at             = event_data.get("cooldown_expire")
    redemptions_redeemed_current_stream = event_data.get("redemptions_redeemed_current_stream")
    logger.debug ("WE DID IT")

def handle_reward_remove (event: dict):
    event_data = event.get("event_data")
    logger.debug(f"handle_reward_remove: EVENT_DATA:{event_data}")
    
    event_id    = event_data.get("id")
    broadcaster_user_id             = event_data.get("broadcaster_user_id")
    broadcaster_user_login          = event_data.get("broadcaster_user_login")
    broadcaster_user_name           = event_data.get("broadcaster_user_name")
    is_enabled                      = event_data.get("is_enabled")
    is_paused                       = event_data.get("is_paused")
    is_in_stock                     = event_data.get("is_in_stock")
    title                           = event_data.get("title")
    cost                            = event_data.get("cost")
    prompt                          = event_data.get("prompt")
    is_user_input_required          = event_data.get("is_user_input_required")
    should_redemptions_skip_request_queue = event_data.get("should_redemptions_skip_request_queue")
    max_per_stream                  = event_data.get("max_per_stream") # 'max_per_stream': {'is_enabled': True, 'value': 100}
    max_per_user_per_stream         = event_data.get("max_per_user_per_stream") #{'is_enabled': True, 'value': 100}
    background_color                = event_data.get("background_color")
    image                           = event_data.get("image")# {'url_1x': 'https://static-cdn.jtvnw.net/image-1.png', 'url_2x': 'https://static-cdn.jtvnw.net/image-2.png', 'url_4x': 'https://static-cdn.jtvnw.net/image-4.png'}
    default_image                   = event_data.get("default_image")
    global_cooldown                 = event_data.get("global_cooldown")#{'is_enabled': True, 'seconds': 300}
    cooldown_expires_at             = event_data.get("cooldown_expire")
    redemptions_redeemed_current_stream = event_data.get("redemptions_redeemed_current_stream")



def handle_reward_update (event: dict):

    event_data = event.get("event_data")
    logger.debug(f"handle_reward_update: EVENT_DATA:{ event_data}")
    
def handle_reward_redemption_add (event: dict):
    event_data = event.get("event_data")
    logger.debug(f"handle_reward_redemption_add EVENT_DATA:{ event_data}")
    reward_id = event_data.get("reward").get("id")
    request_id = event_data.get("id")
    user_id = event_data.get("user_id")
    rewards = get_active_channelpoint_rewards()
#    for reward in rewards:
 #       val = reward[1]
    val2 = event_data.get("reward").get("title")
    if val2=="activate keylogger":
        # -> obs source screenkey active
        logger.debug("got activate keylogger channelpoint-request")
        data = { "event_type":"obs_set_source_visibility", "event_data":{"source_name":"screenkey",
                                                                         "scene_name":"ALERTS",
                                                                         "visible":True}}
        post_event("obs_set_source_visibility",data )        
        # timer start
        # ist schon ein laufender timer aktiv? -> dann add
        post_event("timer_start_event", {"event_name":"screenkey_timer", 
                                         "duration":300, 
                                         "timer_done_event":"obs_set_source_visibility", 
                                         "timer_done_event_data": {"scene_name": "ALERTS", 
                                                                   "source_name": "screenkey", 
                                                                   "visible":False
                                                                   }
                                         }
                   )
        # fulfill
        

    elif val2=="slap":
        f=[]
        fpath = reward[2]
        logger.debug(f"slap_path: {fpath}")
        #files = [x for x in os.listdir(fpath) if os.path.isfile(os.path.isfile(os.path.join(fpath,x)))]
        for x in os.listdir(fpath):
            if os.path.isfile(os.path.join(fpath, x)):
                f.append(x)

        #logger.debug(f"files: {files}, f: {f}")
        mpv_file = random.choice(f)
        logger.debug(f"SLAP_FILE: {mpv_file}")
        slap_data = {"event_type":"obs_set_source_visibility", "event_data":{"scene_name": "raid_overlay", 
                                                                            "source_name": "slap_command",
                                                                             "visible": True}}

        slap_txt = f"{event_data.get("user_name")} slaps {event_data.get("user_input")}"
        gather_task = run_command.GatherTasks()

        gather_task.add_task(lambda: run_mpv(fpath+mpv_file, "100",True ))
        gather_task.add_task(lambda: write_file("/home/sna/5n4fu_stream/data/slap_command.txt", "w", slap_txt))
        gather_task.add_task(lambda: post_event("obs_set_source_visibility",slap_data))
        gather_task.run_tasks()

    elif val2 == "snaAlarm":

            write_snaalert_file(event_data.get("user_input"))
            data = { "event_type":"obs_set_source_visibility", "event_data": {"source_name":"snalarm",
                                                                              "scene_name":"ALERTS",
                                                                              "visible": True}}
            post_event("obs_set_source_visibility", data)
            post_event("timer_start_event", {"event_name":"screenkey_timer", 
                                             "duration":15, 
                                             "timer_done_event":"obs_set_source_visibility", 
                                             "timer_done_event_data": {"scene_name": "ALERTS", 
                                                                       "source_name": "snalarm", 
                                                                       "visible":False
                                                                       }
                                             })


            logger.debug(f"CUSTOM REWARD REDEMPTION: snaAlarm")
    else:
        logger.debug(f"sorry REWARD {val} is not active right now")
                                                                                     

def handle_redemption_update(event: dict):
    event_data = event.get("event_data")
    logger.debug(f"handle_redepmtion_udpate EVENT_DATA:{ event_data}")

# v1 // v2
def handle_automatic_reward_redemption_add(event: dict):
    logger.debug(f"automatic_reward_redemption_add {event}")
