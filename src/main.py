import os
import asyncio
from dotenv import load_dotenv
import events
from events import twitch_events
from dispatcher.event_dispatcher import subscribe_event
import handlers.twitch_event_handler as handler
from utils.run_commands import run_subprocess
from utils import log

def my_event_subscriptions():
    subscribe_event("twitch_subscribe_event", handler.handle_twitch_subscribe_event)
    subscribe_event("twitch_ban_event", handler.handle_twitch_ban_event)
    subscribe_event("twitch_goal_event", handler.handle_twitch_goal_event)
    subscribe_event("twitch_channelpoint_event", handler.handle_twitch_channelpoint_event)
    subscribe_event("twitch_poll_event", handler.handle_twitch_poll_event)
    subscribe_event("twitch_predictions_event", handler.handle_twitch_prediction_event)
    subscribe_event("twitch_hypetrain_event", handler.handle_twitch_hypetrain_event)
    subscribe_event("twitch_shoutout_event", handler.handle_twitch_shoutout_event)

    subscribe_event("twitch_streaminfo_event", handler.handle_twitch_streaminfo_event)
    subscribe_event("twitch_charity_event", handler.handle_twitch_charity_event)
    subscribe_event("twitch_action_events", handler.handle_twitch_action_event)
    subscribe_event("twitch_moderate_event", handler.hanle_twitch_moderate_event)



async def trigger_cli_event(event_key, event_id):

    if event_key.find("channel.update_v2") != -1 or event_key.find("channel.update") != -1 :
        event_key = "channel.update"
        command = f"twitch event trigger {event_key} -u {event_id} -t {os.getenv("CLI_USER_ID")} -v 2 -T websocket"
    elif event_key.find("channel.channel_points_custom_reward_redemption.addv2") != -1:

        command = f"twitch event trigger {event_key} -u {event_id} -t {os.getenv("CLI_USER_ID")} -v 2 -T websocket"
    else:
        command = f"twitch event trigger {event_key} -u {event_id} -t {os.getenv("CLI_USER_ID")} -T websocket"
    
    
    print (f"#######{command}")
    await run_subprocess(command)


async def main():
    #load_dotenv(dotenv_path="/home/sna/src/twitch/events/.env_twitch_events")
    # TODO .envs anpassen
    my_event_subscriptions()
    async with twitch_events.TwitchEvents(dotenv_path= "/home/sna/src/twitch/src/events/.env_twitch_events", use_cli=True) as tevents:
        print (f"dotenv_path: ")
        try:
            #print (type(tevents))
            #test_ids = await tevents.listen_subscribe_events()
            #test_ids = await tevents.listen_ban_events()
            #twitch_ban_event_ids = await tevents.listen_ban_events()
            #test_ids = await tevents.listen_stream_info_events()
            
            
            #test_ids = await tevents.listen_channel_goal_events()
            #test_ids = await tevents.listen_channel_points()
            test_ids = await tevents.listen_channel_polls()
            #test_ids = await tevents.listen_channel_predictions()
            #test_ids = await tevents.listen_hype_train()
            #test_ids = await tevents.listen_shoutout_events()
          
            #test_ids = await tevents.listen_charity_events()
            #test_ids = await tevents.listen_channel_action_events()
            #test_ids = await tevents.listen_channel_moderate_events()

            for x in test_ids:
                await trigger_cli_event(x, test_ids[x])
                
                
        except Exception as e:
            print(e)
            print(f'error while scubscribing........\n\t{e}')
        try:
            while True:
                #print("blub")
                #choice = await display_menu()
                #await choicechecker(choice, tevents)
                await asyncio.sleep(0.1)
         
        except asyncio.CancelledError:
            print("cu later...")

asyncio.run(main())
