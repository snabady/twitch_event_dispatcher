import threading
import os
import asyncio
import logging
import time
from dotenv import load_dotenv
import signal
from events import twitch_events,obsws, event_timer
#from events.obsws import Obsws
from dispatcher.event_dispatcher import subscribe_event
import handlers.twitch_event_handler as twitch_handler
import  handlers.obsws_handler as obsws_handler
import handlers.stream_stats as stream_stats
import handlers.twitchapi_handler as twitchapi_handler
import handlers.sna_irc_handler as sna_irc_handler
from  handlers import db_handler
from handlers import asciiquarium
#from handlers import bait_handler
from handlers import twitchapi
from utils.run_command import run_subprocess
from utils import log
from baitgame.bait import FishGame
from utils.wled import WLEDController
#from data import stream_stats_data
from emotes.display import start_emote_display
from dispatcher.http_event_api import app as http_event

from events import twitch_irc_events
#stream_stats_data = stream_stats_data.ChatStats()


logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   



def my_event_subscriptions():
    subscribe_event("IRC_COMMAND",              sna_irc_handler.handle_chat_command )
    subscribe_event("IRC_JOINED",               sna_irc_handler.handle_irc_joined )
    subscribe_event("IRC_MESSAGE",              sna_irc_handler.handle_irc_message )

async def trigger_cli_event(event_key, event_id):

    if event_key.find("channel.update_v2") != -1 or event_key.find("channel.update") != -1 :
        event_key = "channel.update"
        command = f"twitch event trigger {event_key} -u {event_id} -t {os.getenv("CLI_USER_ID")} -v 2 -T websocket"
    elif event_key.find("channel.channel_points_custom_reward_redemption.addv2") != -1:

        command = f"twitch event trigger {event_key} -u {event_id} -t {os.getenv("CLI_USER_ID")} -v 2 -T websocket"
    elif event_key.find("follow") != -1:
        #for x in range(10):
        command = f"twitch event trigger {event_key} -u {event_id} -t {os.getenv("CLI_USER_ID")} -T websocket"
        #    await run_subprocess(command)
    else:
        command = f"twitch event trigger {event_key} -u {event_id} -t {os.getenv("CLI_USER_ID")} -T websocket"

    logger.debug (f"#######  {command}")
    await run_subprocess(command)



def append_ids(cli_ids, test_ids):
    for ids in test_ids:
        cli_ids[ids] = test_ids[ids]
    return cli_ids

async def cli_twitch_listen():
    async with twitch_events.TwitchEvents(dotenv_path= "/home/sna/src/twitch/src/events/.env_twitch_events", use_cli=True) as tevents:
        try:
            cli_ids = {}
            test_ids = await tevents.listen_subscribe_events()
            cli_ids = append_ids(cli_ids, test_ids)
            test_ids = await tevents.listen_ban_events()
            cli_ids = append_ids(cli_ids, test_ids)
            test_ids = await tevents.listen_channel_goal_events()
            cli_ids = append_ids(cli_ids, test_ids)
            #test_ids = await tevents.listen_channel_points()
            #cli_ids = append_ids(cli_ids, test_ids)
            test_ids = await tevents.listen_channel_polls()
            #cli_ids = append_ids(cli_ids, test_ids)
            #test_ids = await tevents.listen_channel_predictions()
            cli_ids = append_ids(cli_ids, test_ids)
            test_ids = await tevents.listen_hype_train()
            cli_ids = append_ids(cli_ids, test_ids)
            test_ids = await tevents.listen_shoutout_events()
            cli_ids = append_ids(cli_ids, test_ids)
            #test_ids = await tevents.listen_charity_events()
            #cli_ids = append_ids(cli_ids, test_ids)
            test_ids = await tevents.listen_channel_action_events()
            cli_ids = append_ids(cli_ids, test_ids)
            #test_ids = await tevents.listen_channel_moderate_events()
            #cli_ids = append_ids(cli_ids, test_ids)
            test_ids = await tevents.listen_stream_info_events()
            xxx = test_ids
            cli_ids = append_ids(cli_ids, test_ids)
            db_handler.write_cli_params(cli_ids)
            for x in xxx:
                await trigger_cli_event(x, xxx[x]) 
                return 
        except Exception as e:
            logger.debug(e)
            logger.debug(f'CLI-subscription ERROR {e}')
        except asyncio.CancelledError:
            logger.debug("cu later...")

async def twitch_listen_live():
    async with twitch_events.TwitchEvents(dotenv_path= "/home/sna/src/twitch/src/events/.env_twitch_events", use_cli=False) as tevents:
        #logger.debug (f"dotenv_path: ")
        try:
            print (type(tevents))
            test_ids = await tevents.listen_subscribe_events()
            #test_ids = await tevents.listen_ban_events()
            #twitch_ban_event_ids = await tevents.listen_ban_events()
            test_ids = await tevents.listen_stream_info_events()            
            test_ids = await tevents.listen_channel_goal_events()
            test_ids = await tevents.listen_channel_points()
            test_ids = await tevents.listen_channel_polls()
            test_ids = await tevents.listen_channel_predictions()           # 
            test_ids = await tevents.listen_hype_train()
            test_ids = await tevents.listen_shoutout_events()         # 
            #test_ids = await tevents.listen_charity_events()
            test_ids = await tevents.listen_channel_action_events()
            #test_ids = await tevents.listen_channel_moderate_events()
            logger.debug("successfully subscribed 5n4fu events")
        except Exception as e:
            logger.debug(e)
            logger.debug(f'LIVE_EVENTS: 5n4fu error while scubscribing... {e}')

        try:
            while True:
                await asyncio.sleep(0.1)
         
        except asyncio.CancelledError:
            logger.debug("cu later...")

async def obs_listen():

    obs = obsws.Obsws()
    await obs.init_obswebsocket_ws()
    logger.debug(obs)

async def irc_listen():
    sna = twitch_irc_events.Irc("/home/sna/src/twitch/src/events/.env_twitch_irc2")
    task1 = asyncio.create_task( sna.run())
    try:
            asyncio.gather(task1)
    except asyncio.CancelledError:
        logger.debug("irc_listen graceful end")

async def tapi_listen():
    async with twitchapi.myTwitch() as twitch_instance:
        print(f"Angemeldeter Nutzer: {twitch_instance.user.display_name}")
        await twitch_instance.twapi_task_runner()
        while True:
            await asyncio.sleep(1)

async def wled_listen():
    try:
        wled = WLEDController("192.168.0.60")
        await wled.start()
    except asyncio.CancelledError:
        logger.debug("asyncio wled_listen EXIT--->")
        await wled.stop()
        raise
async def emote_loop():
    start_emote_display()

def run_flask():
    try:
        http_event.run(port=5001,use_reloader=False)
    except asyncio.CancelledError:
        print("run_flask what about a graceful end?")


def handle_exit(*args):
    logger.debug(f"handle_exit {args}")
    shutdown_event.set()

shutdown_event = asyncio.Event()

async def main():
    my_event_subscriptions()
    #fishis = FishGame()
    #lask_thread = threading.Thread(target=run_flask, daemon=True)
    #flask_thread.start()
    event_timer.MultiTimerClass()
 
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_exit)

        tasks = [
                #asyncio.create_task( wled_listen() ), 
                #asyncio.create_task( cli_twitch_listen() ),
                #asyncio.create_task( tapi_listen() ),
                asyncio.create_task( irc_listen() )
                #asyncio.create_task( obs_listen() ),
                #asyncio.create_task( twitch_listen_live() )
                ]

        await shutdown_event.wait()

        for task in tasks: 
            task.cancel()
    
        for task in tasks: 
            try:
                await task
            except asyncio.CancelledError:
                print("main cancled")
                pass
#        flask_thread.stop()
        #fishis.end_bait()
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exit...........bye.............cya")

