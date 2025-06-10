import os
import asyncio
from dotenv import load_dotenv
import events
from events import twitch_events
from dispatcher.event_dispatcher import subscribe_event
from handlers.twitch_event_handler import handle_twitch_subscribe_event
from utils.run_commands import run_subprocess
from utils import log

def my_event_subscriptions():
    subscribe_event("twitch_subscribe_event", handle_twitch_subscribe_event)
    subscribe_event("twitch_ban_event", handle_twitch_ban_event)
    subscribe_event("twitch_goal_event", handle_twitch_goal_event)
    subscribe_event("twitch_channelpoint_event", handle_twitch_channelpint_event)
    subscribe_event("twitch_channel_poll", handle_twitch_poll_event)
    subscribe_event("twitch_predictions_event", handle_twitch_prediction_event)
    subscribe_event("twitch_hypetrain_event", handle_twitch_hypetrain_event)
    subscribe_event("twitch_shoutout_event", handle_twitch_shoutout_event)

    subscribe_event("twitch_streaminfo_event", handle_twitch_streaminfo_event)
    subscribe_event("twitch_charity_event", handle_twitch_charity_event)
    subscribe_event("twitch_action_events", handle_twitch_action_event)
    subscribe_event("twitch_moderate_event", hanle_twitch_moderate_event)

async def trigger_cli_event(event_key, event_id):
    
    command = f"twitch event trigger {event_key} -u {event_id} -t {os.getenv("CLI_USER_ID")} -T websocket"
    print (f"---------------------------------------------------------------{command}")
    await run_subprocess(command)


async def main():
    load_dotenv()
    my_event_subscriptions()
    async with twitch_events.TwitchEvents(dotenv_path= (os.getenv("TWITCH_EVENT_DOTENVPATH")), use_cli=os.getenv("USE_CLI")) as tevents:
        try:
            #print (type(tevents))
            subscribe_event_ids = await tevents.listen_subscribe_events()
   
                
            twitch_ban_event_ids = await tevents.listen_ban_events()
            #await tevents.listen_channel_goal_events()
            #await tevents.listen_channel_points()
            #await tevents.listen_channel_polls()
            #await tevents.listen_channel_predictions()
            #await tevents.listen_hype_train()
            #await tevents.listen_shoutout_events()
            #await tevents.listen_stream_info_events()
            ##await tevents.listen_charity_events()
            #await tevents.listen_channel_action_events()
            ##await tevents.listen_channel_moderate_events()

            for x in twitch_ban_event_ids:
                await trigger_cli_event(x, twitch_ban_event_ids[x])
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
