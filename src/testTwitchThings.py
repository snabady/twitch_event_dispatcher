import asyncio
from handlers import twitchapi

async def main():
    async with twitchapi.myTwitch() as twitch_instance:
        print(f"Angemeldeter Nutzer: {twitch_instance.user.display_name}")
        await twitch_instance.get_followers()
        print("-------------------------------------")
        await twitch_instance.get_current_subscribers()
        #await twitch_instance.create_clip()
        await twitch_instance.create_custom_reward()
        while True:
            await asyncio.sleep(1)
            
            

asyncio.run(main())
