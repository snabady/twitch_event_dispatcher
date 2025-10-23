import os
from collections import defaultdict 
import logging
import asyncio
from dotenv import load_dotenv, find_dotenv
from typing import Tuple, Optional,List
from twitchAPI.helper import first
from twitchAPI.type import AuthScope
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.twitch import Twitch, TwitchUser
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from utils import log
from handlers import db_handler
from twitchAPI.type import CustomRewardRedemptionStatus
from dispatcher.event_dispatcher import post_event, subscribe_event


logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)

def trigger_follower_count():
    logger.debug("trigger_follower_count")
    async def runner():
        twapi = myTwitch()
        await twapi.get_follower_count()
    myTwitch().enqueue(runner())

def trigger_sub_count():
    async def runner():
        twapi = myTwitch()
        await twapi.get_sub_count()
    myTwitch().enqueue(runner())

def trigger_send_message(msg):
    async def runner():
        twapi = myTwitch()
        await twapi.send_chat_message(msg)
    myTwitch().enqueue(runner())

def trigger_get_user_id(user_name: str): 
    logger.debug(f"trigger_get_user_id {user_name} type: {type(user_name)}")
    async def runner():
        twapi = myTwitch()
        await twapi.get_user_id(user_name)
    myTwitch().enqueue(runner())

def trigger_create_clip(user_name: str): 
    async def runner():
        twapi = myTwitch()
        await twapi.create_clip()
    myTwitch().enqueue(runner())

def trigger_get_user_profile_imgs(user_names:list):
    async def runner():
        twapi=myTwitch()
        ret = await twapi.get_user_profile_imgs(user_names)
        #post_event("finish_vip_chart_with_profile_pics", ret)
    myTwitch().enqueue(runner())

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        #cls._instances[cls] = super(Singleton, cls).__call__(*args,**kwargs)
        #return cls._instances[cls]
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class myTwitch(metaclass=Singleton):

    def __init__(self, dotenv_path="/home/sna/src/twitch/.env"):
        self.dotenv_path = dotenv_path
        #self.dotenv_path = "/home/sna/src/twitch/src/handlers/.env_twitchapi"
        self.twapi_queue = asyncio.Queue()
        self.logger = logging.getLogger("twitch_REQUESTS  -->>")
        if not self.logger.hasHandlers():
            log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug(f"dotenvpath: {self.dotenv_path}")
        self.scopes = TARGET_SCOPES
        #self.use_cli = use_cli
        #asyncio.create_task(self.twapi_task_runner())
        subscribe_event("trigger_get_user_profile_imgs", trigger_get_user_profile_imgs)
        self.broadcaster_id = None
        self.current_vips = None
        self.session_unfollowed_user_ids = defaultdict(int)
        subscribe_event("stream_online_event", self.set_stream_online)
        self.is_stream_online = False

    async def __aenter__(self):
        self.twitch, self.user = await self.get_twitch_api_conn()
        #asyncio.create_task(self.twapi_task_runner())
        return self
    
    def set_stream_online(self, event_data):
        self.logger.debug(f"setting stream online: {event_data}")
        self.is_stream_online=event_data
    
    async def init_sna(self):
        self.logger.debug("aenter")
        self.twitch, self.user = await self.get_twitch_api_conn()
        self.broadcaster_id = self.get_user_id("5n4fu")

    async def get_user_id(self, user_name):

        x  = await first(self.twitch.get_users(logins=[user_name]))
        
        post_event("twapi_user_id_result", x.id)
        return x.id
    async def get_user_id_str(self, user_name):
        x = await first(self.twitch.get_users(logins=[user_name]))
        return x.id
    async def get_user_profile_imgs (self, user_names: list, callback=None) :
        self.logger.debug(f"**************  get_users: {user_names}")
        user_imgs = defaultdict(str)

        async for user in self.twitch.get_users(logins=user_names):
            #self.logger.debug(f"userdata: {user}")             
            user_imgs[user.display_name] = user.profile_image_url            
        
        post_event("finish_vip_chart_with_profile_pics", user_imgs)    
        return user_imgs    

    async def get_moderators(self):
        b_id = await first(self.twitch.get_users(logins=["5n4fu"]))
        mods = []
        async for mod in self.twitch.get_moderators(b_id.id):
            if not db_handler.check_excisting_twitch_user(mod.user_id):
                user_data = await first(self.twitch.get_users(logins=[mod.user_name]))
                db_handler.add_new_twitch_user([user_data.id, user_data.login, user_data.display_name])

            self.logger.debug(f"moderartor: {mod}")
            mods.append(mod)
        db_handler.update_current_mods(mods)
        
    async def get_vipsis(self):
        b_id = await first(self.twitch.get_users(logins=["5n4fu"]))
        vips =[]
        async for vip in self.twitch.get_vips(b_id.id):
            self.logger.debug(f"vip: {vip.user_id}")
            vips.append(vip)
        db_handler.update_current_vips(vips)
        vips = db_handler.execute_query("select user_name, user_id from special_users where is_vip=1", None)
        self.logger.debug(vips)
        self.current_vips = vips
        
    # TODO RECONNECT OBS EINBAUEN!!!!!!!!!!!!1
    async def twapi_task_runner(self):
        try:
            while True:
                #if self.obs_task_queue.qsize() > 0:
                task_coro_func = await self.twapi_queue.get()
                               
                try:
                    self.logger.debug("twapi_task_runner executing")
                    await task_coro_func# Execute the coroutine
                
                except Exception as e:
                    self.logger.critical(f"TWAPI_TASK_RUNNER Exception: {e}", exc_info=True)      
                    
                finally:
                    self.twapi_queue.task_done()   
                    self.logger.debug(f"twapi-queue-size: {self.twapi_queue.qsize()}")
                await asyncio.sleep(0.5)
               
        except Exception as e:
            self.logger.critical(f"TWAPI_TASK_RUNNER Exception: {e}", exc_info=True)

    def enqueue(self, coro):
        self.logger.debug(f"~~~~~~~enqueued:{coro} {coro.__name__}")
        self.twapi_queue.put_nowait(coro)
        #self.logger.debug(f"after put: twapi queue size: {self.twapi_queue.qsize()}")

    async def dispatch_twitch_event(self, event ):
        event_source = "twitch_event"
        ts = datetime.datetime.now()
        data = ""
        #self.logger.debug(f'x: {type(x)}') #s
        if self.event_map[type(x)] != None:
            self.logger.debug(f"dispatching **** event_type:-----------------> >>> {x.subscription.type} <<<")
            data = {
                "timestamp_received": ts, 
                "event_source": event_source,
                "event_type": x.subscription.type,
                "type": self.event_map[type(x)],
                "event_data": x.event.to_dict()
            }
            
            self.logger.debug(f"POST:{self.event_map[type(x)]} ")
            post_event(self.event_map[type(x)], data)
    
    async def send_chat_message(self, message):
        await self.twitch.send_chat_message(self.user.id, self.user.id, message)

    async def __aexit__(self, exc_type,exc_val, exc_tb):
        await self.twitch.close()

    async def auth_token_generator(self, twitch: Twitch, USER_SCOPE) -> (str, str):
        redirection_url ="http://localhost:17561"
        auth = UserAuthenticator(twitch, self.scopes,url=redirection_url,  host='0.0.0.0', port=17561)
        token, refresh_token = await auth.authenticate()
        #self.logger.debug(f"{token}")
        return token, refresh_token

    async def get_twitch_api_conn(self) -> Tuple[ Twitch, TwitchUser]:
        self.logger.debug(f"dotenv_path: {self.dotenv_path}")
        auth_base_url = os.getenv("TWAPI_AUTH_BASE_URL", "ERROR_AUTH_BASE_URL")
        twitch = await Twitch(os.getenv("TWAPI_CLIENT_ID"), os.getenv("TWAPI_CLIENT_SECRET"))


        #helper = UserAuthenticationStorageHelper(twitch, self.scopes, storage_path="/home/sna/src/twitch-irc/auth_storage/snarequests.json", auth_generator_func=self.auth_token_generator)#/home/sna/src/twitch/auth_storage
        helper = UserAuthenticationStorageHelper(twitch, self.scopes, storage_path=os.getenv("TWAPI_AUTH_STORAGE_FILE"), auth_generator_func=self.auth_token_generator)
        await helper.bind()
        user = await first(twitch.get_users())

        return twitch, user


    async def create_timeout(self, user_id: int, reason: str, duration: int):
        self.broadcaster_id = await self.get_user_id_str("5n4fu")
        await self.twitch.ban_user(str(self.broadcaster_id), str(self.broadcaster_id), user_id, reason, duration)
    
    async def check_unfollows(self):
        await self.get_followers()
        query="SELECT f.user_id, u.user_name FROM followerlist f left join twitch_users u on f.user_id=u.user_id LEFT JOIN current_followers c ON f.user_id = c.user_id where c.user_id is null"
        #result = db_handler.execute_query("SELECT f.user_id, f.user_name FROM followerlist f LEFT JOIN current_followers c ON f.user_id = c.user_id WHERE c.user_id IS NULL", None) 
        result = db_handler.execute_query(query, None)
        #result = db_handler.execute_query("select  u.user_id , u.user_name from twitch_users u right join unfollowed_users c on u.user_name=c.user_name", None) # debug query
        self.logger.debug(f"unfollows: {result}")
        #result = [[102784092, "teekay84"]] # debug for one
        for user in result:
            unfollow_user_id = user[0]
            unfollow_user_name = user[1]
            if unfollow_user_id in self.session_unfollowed_user_ids:
                if self.session_unfollowed_user_ids[unfollow_user_id] >= 666:
                    multiplicator = self.session_unfollowed_user_ids[unfollow_user_id] - 666 + 1
                    timeout_duration = multiplicator*multiplicator * 300
                    msg =f"well... timeout for: {unfollow_user_name} for -abusing unfollow event- for {timeout_duration}seconds"
                    await self.create_timeout(unfollow_user_id, "abusing unfollow event", timeout_duration)
                    self.session_unfollowed_user_ids[unfollow_user_id] += 1
                else:
                    msg = f"{unfollow_user_name} one unfollow per day is enough, right? do it again and u will get a timeout"
                    self.session_unfollowed_user_ids[unfollow_user_id] = 666
                    db_handler.remove_from_followerlist(unfollow_user_id)
            else:
                # trigger event fishifood-event with some sound ohno.. ohno... ohnonononono
                self.session_unfollowed_user_ids[unfollow_user_id] = 1
                db_handler.add_unfollow(unfollow_user_id)
                msg = f"thank you {unfollow_user_name} for your unfollow. you have gotten into fresh fishi-food"
                post_event("trigger_ascii_rain", 42)
                post_event("trigger_event_board", "ohno.mp3")
            print(msg)
            post_event("irc_send_message",msg)
            
    async def get_followers(self):
        # MODERATOR_READ_FOLLOWERS
        self.logger.info("get followers????")
        result = await self.twitch.get_channel_followers(self.user.id)
        self.logger.info(f"total_followers: {result.total}")
        follower_ids =[]
        
        async for x in result:
            follower_ids.append(x.user_id) 
            
        db_handler.update_current_follower(follower_ids)
    
    async def get_follower_count(self):
        result = await self.twitch.get_channel_followers(self.user.id)
        await self.get_followers()
        data = { "event_type" : "follower_count", 
                "event_data" : {"total_follower": result.total} }
        self.logger.info(f"xx total_followers: {result.total}")
        post_event("twitchapi_follower_counter", data)
        

    async def create_clip(self):
        clip = await self.twitch.create_clip(self.user.id)
        clip_id =clip.id 
        clip_edit_url = clip.edit_url
        self.logger.debug(f"CLIP: {clip_edit_url} id: {clip_id}")
    
    async def get_current_subscribers(self):
        subscribers = await self.twitch.get_broadcaster_subscriptions(self.user.id)
        self.logger.info (f"subcount:  {subscribers.total}")
        async for x in subscribers:
            self.logger.debug(f"subs: {x.user_name}")

                #await self.twitch.create_custom_reward(broadcaster_id=self.user.id, title="testing twitchAPI create custom reward", cost=100, is_enabled=True,prompt="snablahblub", is_user_input_required=True,is_max_per_user_per_stream_enabled=True, global_cooldown_seconds=500, max_per_user_per_stream=1)
        #await self.twitch.create_stream_marker()
        
        res =  self.twitch.get_user_block_list(self.user.id)
        async for x in res : 
            self.logger.debug(x)
        
        res = self.twitch.get_creator_goals(self.user.id)
        async for x in res :
            self.logger.debug(x)
        res = await self.twitch.get_chatters(broadcaster_id=self.user.id, moderator_id=self.user.id)
        async for x in res:
            self.logger.debug(x.user_name)
        #self.twitch.get_game_analytics()
        #self.twitch.
        
        
    async def get_sub_count(self):
        subscribers = await self.twitch.get_broadcaster_subscriptions(self.user.id)
        self.logger.info (f"subcount:  {subscribers.total}")
        data = { "event_type" : "sub_count", 
                 "event_data" : {"total_subs": subscribers.total} }
        for x in data:
            self.logger.debug(f"sub: {x}")
        self.logger.info(f"xx total_subs: {subscribers.total}")
        post_event("twitchapi_sub_count", data)

    async def create_custom_reward(self):

        #raise NotImplementedError
       # x = await first (self.twitch.get_custom_reward_redemption(broadcaster_id= self.user.id,
       #                                                           status=CustomRewardRedemptionStatus.UNFULFILLED,
       #                                                           reward_id="7dfeb87a-ef51-47f3-b6b1-f476d7ea14f1"))
       # self.logger.debug(x)

        #res = await update_redemption_status(broadcaster_id=self.user.id, reward_id="", redemption_ids, status)
        await self.twitch.create_custom_reward(broadcaster_id=self.user.id, 
                                               title="your offline flash", 
                                               background_color="#ffffff",
                                               cost=1001, 
                                               is_enabled=True,
                                               prompt="why?", 
                                               is_user_input_required=False,
                                               #is_max_per_user_per_stream_enabled=True,
                                               #max_per_user_per_stream=1,
                                               is_global_cooldown_enabled=False, 
                                               should_redemptions_skip_request_queue=True)
        
    async def create_stream_marker(self):
        await self.twitch.create_stream_marker()

    # broadcaster_id, reward_id, redemption_ids, status (ids: Union/list/str
    async def update_redemption_status(self):
        self.twitch.update_redemption_status(self.user_id, )
        

TARGET_SCOPES = [
                 AuthScope.MODERATOR_READ_FOLLOWERS,
                 AuthScope.USER_READ_CHAT,
                 AuthScope.CHANNEL_BOT, 
                 AuthScope.USER_READ_EMOTES,
                 AuthScope.CHAT_READ, 
                 AuthScope.CHAT_EDIT,
                 AuthScope.CHANNEL_MODERATE,
                 AuthScope.USER_READ_EMAIL,
                 AuthScope.MODERATOR_READ_FOLLOWERS,
                 AuthScope.CHANNEL_MANAGE_POLLS,
                 AuthScope.CHANNEL_READ_GOALS,
                 AuthScope.CHANNEL_READ_ADS,
                 AuthScope.CHANNEL_MODERATE,
                 AuthScope.USER_BOT,
                 AuthScope.BITS_READ,
                 AuthScope.MODERATOR_READ_BLOCKED_TERMS,
                 AuthScope.MODERATOR_READ_CHAT_SETTINGS,
                 AuthScope.MODERATOR_READ_MODERATORS,
                 AuthScope.MODERATOR_READ_VIPS,
                 AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS,
                 AuthScope.MODERATOR_MANAGE_BANNED_USERS,
                 AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES,
                 AuthScope.MODERATOR_MANAGE_WARNINGS,
                 AuthScope.CHANNEL_MANAGE_VIPS,
                 AuthScope.MODERATION_READ,
                 AuthScope.CHANNEL_MANAGE_POLLS,
                 AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS,
                 AuthScope.CHANNEL_MANAGE_PREDICTIONS,
                 AuthScope.CHANNEL_MANAGE_REDEMPTIONS,
                 AuthScope.MODERATOR_MANAGE_AUTOMOD,
                 AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
                 AuthScope.CHANNEL_READ_HYPE_TRAIN,
                 AuthScope.MODERATOR_MANAGE_SHIELD_MODE,
                 AuthScope.MODERATOR_READ_SUSPICIOUS_USERS,
                 AuthScope.MODERATOR_MANAGE_WARNINGS,
                 AuthScope.MODERATOR_READ_AUTOMOD_SETTINGS,
                 AuthScope.MODERATOR_MANAGE_SHOUTOUTS, 
                 AuthScope.CLIPS_EDIT, 
                 AuthScope.CHANNEL_READ_SUBSCRIPTIONS, 
                 AuthScope.MODERATOR_READ_CHATTERS,
                 AuthScope.CHANNEL_READ_GOALS,
                 AuthScope.USER_READ_BLOCKED_USERS,
                 AuthScope.USER_WRITE_CHAT,
                 AuthScope.CHANNEL_READ_REDEMPTIONS,
                 AuthScope.CHANNEL_READ_VIPS
                 ]
