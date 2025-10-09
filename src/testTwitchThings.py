import asyncio
from handlers import twitchapi
from dispatcher.event_dispatcher import subscribe_event, post_event
from handlers.twitchapi import trigger_get_user_profile_imgs
from handlers.custom_rewards_manager import ChannelPointManager
async def main():
    
    async with twitchapi.myTwitch() as twitch_instance:
        print(f"Angemeldeter Nutzer: {twitch_instance.user.display_name}")
        asyncio.create_task(twitch_instance.twapi_task_runner())
        #await twitch_instance.twapi_task_runner()
        await twitch_instance.get_followers()
        print("-------------------------------------")
        #await twitch_instance.get_current_subscribers()
        #await twitch_instance.create_clip()
        #result = post_event("trigger_get_user_profile_imgs", ["legomen68","5n4fu","snabady","snabotski"])

        #await twitch_instance.get_moderators()
        #await twitch_instance.get_vipsis()
        #await twitch_instance.create_custom_reward()
        #res = await result
        #print (f"result: {res}")
        #await twitch_instance.get_user_profile_imgs(["5n4fu","snabady","snabotski"])

        print("registering channel_point_manager")
        channel_points_manager = ChannelPointManager(twitch_instance)
        #await channel_points_manager.create_custom_rewardx()
        #await channel_points_manager.delete_custom_reward("edac1750-0c5e-43de-a723-482d5c8a946b")
        await channel_points_manager.deactivate_reward_category(1)
        await channel_points_manager.deactivate_reward_category(5, True)
        print ("NICE..........................")

        await channel_points_manager.get_custom_reward()
        while True:
            await asyncio.sleep(1)
        print (result)
            
            

asyncio.run(main())
