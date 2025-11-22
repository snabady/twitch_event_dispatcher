from dotenv import load_dotenv
DOTENV_PATH="/home/sna/src/twitch/.env"
from dotenv import load_dotenv
load_dotenv(DOTENV_PATH)

import asyncio
from handlers import twitchapi, db_handler
from dispatcher.event_dispatcher import subscribe_event, post_event
from handlers.twitchapi import trigger_get_user_profile_imgs
from handlers.custom_rewards_manager import ChannelPointManager
from utils import run_command
async def main():
    
    async with twitchapi.myTwitch() as twitch_instance:
        print(f"Angemeldeter Nutzer: {twitch_instance.user.display_name}")
        asyncio.create_task(twitch_instance.twapi_task_runner())
        #await twitch_instance.twapi_task_runner()
        #await twitch_instance.get_followers()
        #print("-------------------------------------")
        #await twitch_instance.get_current_subscribers()
        #await twitch_instance.create_clip()
        #result = post_event("trigger_get_user_profile_imgs", ["legomen68","5n4fu","snabady","snabotski"])

        #await twitch_instance.get_moderators()
        #await twitch_instance.get_vipsis()
        #await twitch_instance.create_custom_reward()
        #res = await result
        #print (f"result: {res}")
        #await twitch_instance.get_user_profile_imgs(["5n4fu","snabady","snabotski"])

        #print("registering channel_point_manager")
       # channel_points_manager = ChannelPointManager(twitch_instance)
        #await channel_points_manager.create_custom_rewardx()
        #await channel_points_manager.delete_custom_reward("edac1750-0c5e-43de-a723-482d5c8a946b")
#        await channel_points_manager.deactivate_reward_category(1)
#        await channel_points_manager.deactivate_reward_category(5, True)

        
        #a+wait channel_points_manager.get_custom_reward()
      #  |await channel_points_manager.deactivate_reward_category(5, True)
       # await channel_points_manager.deactivate_reward_category(1, False)
        #db_handler.handle_get_followage([1235361075])
        # unfollow-tests
        #await twitch_instance.check_unfollows()
        #result = db_handler.execute_query("selct * from unfollow_events where user_id=1234", None)
        #print (result)
        #print (len(result))

        #run_command.create_epaper_vip_badge({"user_name":"Fluffiy","vip_user_image":"https://static-cdn.jtvnw.net/jtv_user_pictures/1f4a4f68-037f-4044-a66d-12bb7c0d1dac-profile_image-300x300.png"}) 
        twitchapi.trigger_update_vip_epaper("Fluffiy_")
        while True:
            await asyncio.sleep(1)
        print (result)
            
            

asyncio.run(main())
