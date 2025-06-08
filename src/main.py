import events
from events import twitch_events




async def main():

    async with twitch_events.TwitchEvents(use_cli_conn=True, dotenv_path="src/events/.env_twitch_events") as tevents:
        try:
            await tevents.listen_subscribe_events()
            await tevents.listen_ban_events()
            await tevents.listen_channel_goal_events()
            await tevents.listen_channel_points()
            await tevents.listen_channel_polls()
            await tevents.listen_channel_predictions()
            await tevents.listen_hype_train()
            await tevents.listen_shoutout_events()
            await tevents.listen_stream_info_events()
            #await tevents.listen_charity_events()
            await tevents.listen_channel_action_events()
            #await tevents.listen_channel_moderate_events()
        except Exception as e:
            print(e)
            print(f'error while scubscribing........\n\t{e}')
        try:
            while True:
                #choice = await display_menu()
                #await choicechecker(choice, tevents)
                await asyncio.sleep(0.1)
         
        except asyncio.CancelledError:
            print("cu later OOO")

asyncio.run(main())
