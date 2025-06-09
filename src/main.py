import os
from dotenv import load_dotenv
import events
from events import twitch_events
import asyncio
from dispatcher.event_dispatcher import subscribe_event
from handlers.twitch_event_handler import handle_twitch_subscribe_event


async def main():
    load_dotenv()

    subscribe_event("twitch_subscribe_event", handle_twitch_subscribe_event)


    async with twitch_events.TwitchEvents(dotenv_path= (os.getenv("TWITCH_EVENT_DOTENVPATH")), use_cli=os.getenv("USE_CLI")) as tevents:
        try:
            #print (type(tevents))
            subscribe_event_ids = await tevents.listen_subscribe_events()
            for key in subscribe_event_ids:
                print(f"{key}: {subscribe_event_ids[key]}")
            #await tevents.listen_ban_events()
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
