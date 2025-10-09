import threading
import asyncio
from dispatcher.event_dispatcher import post_event, subscribe_event
from handlers import db_handler
from handlers.twitchapi import myTwitch
import logging
from utils import log

class ChannelPointManager:

    # - streamstart -> alle channelpoint rewars, welche fuer die category passen einfuegen
    # - streamend   -> offline-rewards aktivieren und alle anderen deaktivieren
    # - rewards erstellen -> in db speichern 
    # - rewards loeschen

    # rewards fullfillment, einloesen handlen
    #
    def __init__(self, twitch_api: myTwitch):
        self.twitch = twitch_api
        self.logger = logging.getLogger("ChannelPointManager")
        if not self.logger.hasHandlers():
            log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)
        self.loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(self.loop)
        self.loop_thread = threading.Thread(target=self._start_loop, daemon=True)
        self.loop_thread.start()
        self.logger.debug("hm")
        subscribe_event("stream_online_event", self.on_stream_online)
        subscribe_event("stream_offline_event", self.on_stream_offline)
        self.logger.debug("subscribed to stream_online_event -----------------------######################################################### ")

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()    
    async def __aenter__(self):
        self.logger.debug("ChannelPointManager aenter")
        self.twitch, self.user = await self.get_twitch_api_conn()
        #asyncio.create_task(self.twapi_task_runner())
        
        return self
 
    async def create_custom_rewardx(self, 
                                    title="default title", 
                                    background_color=None, 
                                    cost=666, 
                                    is_enabled=False, 
                                    prompt=None,
                                    is_user_input_required=False,
                                    max_per_stream=None,
                                    is_max_per_user_per_stream_enabled=False,
                                    max_per_user_per_stream=None,
                                    is_global_cooldown_enabled=False, 
                                    global_cooldown_seconds=None,
                                    should_redemptions_skip_request_queue=False):


        custom_reward = await self.twitch.twitch.create_custom_reward(broadcaster_id=self.twitch.user.id, 
                                               title=title, 
                                               background_color="#ffffff",
                                               cost=1001, 
                                               is_enabled=True,
                                               prompt="why?", 
                                               is_user_input_required=False,
                                               #is_max_per_user_per_stream_enabled=True,
                                               #max_per_user_per_stream=1,
                                               is_global_cooldown_enabled=False, 
                                               should_redemptions_skip_request_queue=True)

        print(custom_reward)
    
    def on_stream_offline(self, event_data):
        self.logger.debug("the stream just went OFFline you should do some stfuff with your custom rewards")
        self.logger.debug(event_data)
        asyncio.run_coroutine_threadsafe(
            self.deactivate_reward_category(reward_category_id=1, enable=False),
            self.loop
        )
        asyncio.run_coroutine_threadsafe(
            self.deactivate_reward_category(reward_category_id=5, enable=True),
            self.loop
        )

    def on_stream_online(self, event_data):
        self.logger.debug("the stream just went online you should do some stfuff with your custom rewards")
        self.logger.debug(event_data)
        asyncio.run_coroutine_threadsafe(
            self.deactivate_reward_category(reward_category_id=1, enable=True),
            self.loop)
        asyncio.run_coroutine_threadsafe(
            self.deactivate_reward_category(reward_category_id=5, enable=False),
            self.loop)

    async def deactivate_reward_category(self, reward_category_id, enable=False ):
        self.logger.debug("deactivate_reward_category")
        for reward in db_handler.execute_query(f"select id,name from custom_rewards where reward_type = {reward_category_id}", None):

            await self.twitch.twitch.update_custom_reward(self.twitch.user.id, reward[0], is_enabled=enable)
            self.logger.debug(f"enable: {enable} category:{reward_category_id} for event: {reward[1]}")

    async def update_custom_reward():
        raise NotImplementedError


    async def delete_custom_reward(self, reward_id: str):
        await self.twitch.twitch.delete_custom_reward(self.twitch.user.id, reward_id)

    async def get_custom_reward_redemption():
        raise NotImplementedError

    """
    gets all current channel rewards, updates database
    """
    async def get_custom_reward(self):
        rewards = await self.twitch.twitch.get_custom_reward(self.twitch.user.id)
        for reward in rewards:
            print(f"{reward.title}, {reward.id}, {reward.is_enabled}")
            print("------------------------------------------------------------------")
        db_handler.update_current_channelpoint_reward(rewards)
