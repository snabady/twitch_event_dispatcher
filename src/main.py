
import asyncio
import logging
from dotenv import load_dotenv
from events import twitch_events,obsws, irc_events
#from events.obsws import Obsws
from dispatcher.event_dispatcher import subscribe_event
import handlers.twitch_event_handler as twitch_handler
import  handlers.obsws_handler as obsws_handler
import handlers.stream_stats as stream_stats
import handlers.twitchapi_handler as twitchapi_handler
import handlers.sna_irc_handler as sna_irc_handler
from  handlers import db_handler
from handlers import bait_handler
from handlers import twitchapi
from utils.run_command import run_subprocess
from utils import log
from baitgame.bait import FishGame
from utils.wled import WLEDController
#from data import stream_stats_data

#stream_stats_data = stream_stats_data.ChatStats()


logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   



def my_event_subscriptions():
    subscribe_event("twitch_subscribe_event", twitch_handler.handle_twitch_subscribe_event)
    subscribe_event("twitch_ban_event", twitch_handler.handle_twitch_ban_event)
    subscribe_event("twitch_goal_event", twitch_handler.handle_twitch_goal_event)
    subscribe_event("twitch_channelpoint_event", twitch_handler.handle_twitch_channelpoint_event)
    subscribe_event("twitch_polql_event", twitch_handler.handle_twitch_poll_event)
    subscribe_event("twitch_predictions_event", twitch_handler.handle_twitch_prediction_event)
    subscribe_event("twitch_hypetrain_event", twitch_handler.handle_twitch_hypetrain_event)
    subscribe_event("twitch_shoutout_event", twitch_handler.handle_twitch_shoutout_event)

    subscribe_event("twitch_streaminfo_event", twitch_handler.handle_twitch_streaminfo_event)
    subscribe_event("twitch_charity_event", twitch_handler.handle_twitch_charity_event)
    subscribe_event("twitch_action_event", twitch_handler.handle_twitch_action_event)
    subscribe_event("twitch_moderate_event", twitch_handler.hanle_twitch_moderate_event)
    
    subscribe_event("twitch_streaminfo_event", obsws_handler.handle_twitch_streaminfo_event)
    subscribe_event("stream_online_event", sna_irc_handler.handle_stream_online)
    subscribe_event("twitchapi_follower_counter", twitchapi_handler.handle_follower_count)
    subscribe_event("twitchapi_sub_count", twitchapi_handler.handle_sub_count)

    subscribe_event("irc_chat_command", sna_irc_handler.handle_chat_command )
    subscribe_event("irc_chat_event", sna_irc_handler.handle_chat_event)
    subscribe_event("chat_command", sna_irc_handler.handle_chat_command)
    subscribe_event("fish_result", bait_handler.handle_fish_result)
    #subscribe_event("followage_command", sna_irc_handler.handle_followage_command)
    subscribe_event("db_get_followage_by_user", db_handler.handle_get_followage_by_user) 
    subscribe_event("twapi_user_id_result", db_handler.handle_get_followage)
    subscribe_event("snafu_flash_event", sna_irc_handler.handle_snafu_flash_event)

    #subscribe_event("irc_bait_event", bait_game.handle_bait)
    #subscribe_event("twitch_stream_info_event", stream_stats.handle_twitch_streaminfo_event)
    

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
    

async def twitch_listen():
    #load_dotenv(dotenv_path="/home/sna/src/twitch/events/.env_twitch_events")
    # TODO .envs anpassen
    
    my_event_subscriptions()
    async with twitch_events.TwitchEvents(dotenv_path= "/home/sna/src/twitch/src/events/.env_twitch_events", use_cli=True) as tevents:
        #logger.debug (f"dotenv_path: ")
        try:
            
            #print (type(tevents))
            #test_ids = await tevents.listen_subscribe_events()
            #test_ids = await tevents.listen_ban_events()
            #twitch_ban_event_ids = await tevents.listen_ban_events()
            test_ids = await tevents.listen_stream_info_events()
            
            
            #test_ids = await tevents.listen_channel_goal_events()
            #test_ids = await tevents.listen_channel_points()
            #test_ids = await tevents.listen_channel_polls()
            #test_ids = await tevents.listen_channel_predictions()
            
            #test_ids = await tevents.listen_hype_train()
            #test_ids = await tevents.listen_shoutout_events()
          
            #test_ids = await tevents.listen_charity_events()
            test_ids = await tevents.listen_channel_action_events()
            #test_ids = await tevents.listen_channel_moderate_events()

            for x in test_ids:
                await trigger_cli_event(x, test_ids[x])
                #break

                #break
            
                
        except Exception as e:
            logger.debug(e)
            logger.debug(f'twitch-listen: error while scubscribing... {e}')

        try:
            while True:
                await asyncio.sleep(0.1)
         
        except asyncio.CancelledError:
            logger.debug("cu later...")



async def twitch_listen_live():
    #load_dotenv(dotenv_path="/home/sna/src/twitch/events/.env_twitch_events")
    # TODO .envs anpassen
    
    my_event_subscriptions()
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
            test_ids = await tevents.listen_channel_predictions()
           # 
            test_ids = await tevents.listen_hype_train()
            test_ids = await tevents.listen_shoutout_events()
         # 
            #test_ids = await tevents.listen_charity_events()
            test_ids = await tevents.listen_channel_action_events()
            #test_ids = await tevents.listen_channel_moderate_events()
            logger.debug("successfully subscribed for 5n4fu AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
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
    
    #asyncio.create_task(obs.obs_task_worker())
    logger.debug(obs)

async def tapi_listenxxx():
    #async with twitchapi.myTwitch() as twitch_instance:
    twitch_instance = twitchapi.myTwitch()
    try:
        await twitch_instance.init_sna()
        logger.debug(f"Angemeldeter Nutzer: {twitch_instance.user.display_name}")
        await twitch_instance.twapi_task_runner()
    except Exception as e: 

        logger.debug("ARGHSDLAKSDJFLAKSJDFASKLF")

async def tapi_listen():
    #async with twitchapi.myTwitch() as twitch_instance:
    twitch_instance = twitchapi.myTwitch()
    try:
        await twitch_instance.init_sna()
        logger.debug(f"Angemeldeter Nutzer: {twitch_instance.user.display_name}")
        await twitch_instance.twapi_task_runner()
    except Exception as e: 

        logger.debug("ARGHSDLAKSDJFLAKSJDFASKLF")

async def irc_listen():

    
    
    sna = irc_events.Irc()
    
    asyncio.create_task( sna.run())
    asyncio.create_task(sna.irc_task_runner())

"""async def main():
    fishis = FishGame()
    await asyncio.gather(obs_listen(),twitch_listen(), tapi_listen(), irc_listen())
    await asyncio.gather(obs_listen(),twitch_listen(), tapi_listen(), twitch_listen_live())

asyncio.run(main())
"""

async def tapi_listen():
    async with twitchapi.myTwitch() as twitch_instance:
        print(f"Angemeldeter Nutzer: {twitch_instance.user.display_name}")
        await twitch_instance.twapi_task_runner()
        while True:
            await asyncio.sleep(1)

async def main():
    fishis = FishGame()
    wled = WLEDController("192.168.0.60")
    await asyncio.gather(obs_listen(),twitch_listen(),  tapi_listen(),irc_listen())
    #await asyncio.gather( twitch_listen(), tapi_listen(), irc_listen(), obs_listen(), twitch_listen_live())
    #await asyncio.gather()
asyncio.run(main())
