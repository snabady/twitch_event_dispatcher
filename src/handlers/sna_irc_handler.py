import random
import requests
import logging
from utils import log
from handlers import db_handler 
import asyncio
from twitchAPI.chat import ChatCommand, JoinEvent, LeftEvent
from dispatcher.event_dispatcher import post_event
#from baitgame.bait import FishGame
logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   
import threading
from utils.run_command import run_xcowsay, run_tts, run_mpv


loop = asyncio.new_event_loop()
t = threading.Thread(target=loop.run_forever, daemon=True)
t.start()

async def handle_ready_event():
    #post_event("set_stream_online", {"event_data": True}) 
    self.logger.debug(f"hello from on_ready: {type(EventData)}")
    await event.chat.join_room(os.getenv("IRC_BOT_CHANNEL_JOIN"))
    self.broadcaster_id = await self.getUser("5n4fu")
    self.user_id = await self.getUser("snabotski")

def handle_chat_event(event_data):
    logger.debug("handle_chat_event")

def handle_irc_message(e_data):
    event_data = e_data.get("event_data") 
    irc_instance = e_data.get("irc_instance")

    text = event_data.text
    logger.debug(f"can we get the message: {text}")
    for x in msg_reaction_functions:
        if text.find(x) > -1:
            msg_reaction_functions[x](event_data, irc_instance)
    irc_instance.stream_stats_data.process_msg(event_data)
def handle_stream_online(e_data):
    logger.debug("FIND OUJT WHAT HAPPENED HERE")

def handle_irc_joined( e_data ):
    event_data = e_data.get("event_data")
    irc_instance = e_data.get("irc_instance")
    #asyncio.run_coroutine_threadsafe(write_chat_msg("oink", irc_instance), loop)

def handle_chat_command(e_data):
    event_data = e_data.get("event_data")
    irc_instance = e_data.get("irc_instance")
    logger.debug(f"event_data {event_data}")
    
    if event_data.name in irc_instance.auto_commands:
        post_event("irc_send_message", irc_instance.auto_commands.get(event_data.name))

    elif event_data.name == "bait":
        logger.debug("ajo it is a bait")
        post_event("fish_bait",event_data.user.display_name)
        post_event("add_bait_led",{"event_data":"add_bait_led_event_data"})
    
    elif event_data.name == "fishisleft":
        post_event("fishis_left", event_data)
    
    elif event_data.name == "flash":
        if any (name == event_data.user.display_name for name, _ in irc_instance.current_vips):
            post_event("snafu_flash_event", {"sna"})
            self.logger.debug("flash received.. user was vip")
        else:
            msg = "sorry you are no vip, try more bait to increase your chances vor VIP"
            post_event("irc_send_message", msg)
        pass

    elif event_data.name == "currentvips":
        c_vips = "current vips"
        for x in irc_instance.current_vips:
            c_vips +=" | "
            c_vips += str(x[0]) 

        post_event("irc_send_message", c_vips)
    
    elif event_data.name == "sna":
        run_xcowsay("/home/sna/5n4fu_stream/media/img/sna.png", event_data.text.replace("!sna","",1), 15, 0, False)
    elif event_data.name == "refresh":
        post_event("get_score_chart_values", "blub")
    elif event_data.name == "tts":
        run_tts(event_data.text)

    elif event_data.name == "mytopbait":
        if event_data.parameter == "1":
            post_event("mytopbait_command_maxgramm", { "event_type" : "mytopbait_command_maxgram",
                                                       "event_data" : event_data.user.display_name } )
        elif event_data.parameter == "2":
            # TODO ?? not working for user/mod? for me working
            post_event("mytopbait_command_personal", { "event_type" : "mytopbait_command_personal",
                                                       "event_data" : event_data.user.display_name } )
        else:
            post_event("mytopbait_command", {"event_type": "mytopbait_command",
                                             "event_data": event_data.user.display_name } )

    elif event_data.name == "topbait":
        post_event("topbait_command", {"event_type": "topbait_command", 
                                       "event_data": event_data.user.display_name })

    elif event_data.name == "mybaitstats":
        post_event("mybaitstats_command", {"event_type":"mybaitstats_command",
                                           "event_data":event_data.user.display_name})

    elif event_data.name == "cmds":
        msg = "commands: "
        for x in irc_instance.cmd_list:
            msg += "!" + x[0] + " | "
        post_event("irc_send_message", msg[0:len(msg)-2])

    elif event_data.name == "followage":
        post_event("db_get_followage_by_user", {"user_name": event_data.user.display_name})

    elif event_data.name == "stats":
        msg = irc_instance.stream_stats_data.get_stats_str()
        post_event("irc_send_message", msg)

def handle_followage_command(event_data):
    logger.debug("handle_followage_command")
    logger.debug(f'event_data: {event_data}')
    

def handle_flash_event(event_data, irc_instance):
    logger.debug("Flash event received...")
    if any (name == event_data.user.display_name for name, _ in irc_instance.current_vips):
        post_event("snafu_flash_event", {"sna"})
        self.logger.debug("flash received.. user was vip")
    else:
        msg = "sorry you are no vip, try more bait to increase your chances vor VIP"
        post_event("irc_send_message", msg)

    update_flash_counter(1)

def handle_bobr_event(event_data, irc_instance):
    #run_mpv("/home/sna/5n4fu_stream/media/vids/bobr_marley.webm", 50)

    requests.get("http://localhost:8000/play?sound=webm/bobr.webm") 
def handle_lightning_event(event_data, irc_instance):
    #asyncio.run_coroutine_threadsafe(write_chat_msg("KEKW lego", irc_instance), loop)
    post_event("irc_send_message", "KEKW")

def handle_hungry_event(event_data, irc_instance):
    # the cat is hungry... take care of your fish
    
    requests.get("http://localhost:8000/play?sound=webm/hangry.webm") 
    if random.choice([True,False]):
        #obs-setsourcevisibility.
        logger.debug("you should trigger hangry now and build a game of it")

def handle_irc_join(e_data):
    logger.debug(f" {e_data.get("event_data").user_name} joined")
    event_data = e_data.get("event_data")
    irc_instance = e_data.get("irc_instance")
    irc_instance.stream_stats_data.add_channel_join(event_data.user_name)

def handle_irc_left(event_data):
    logger.debug(f"{event_data.get("event_data").user_name} left")
# TODO move to db
msg_reaction_functions = {
        "FLASH":handle_flash_event,
        "lightning":handle_lightning_event,
        "!lightning":handle_lightning_event,
        "!hungry":handle_hungry_event,
        "!bobr": handle_bobr_event
        } 


