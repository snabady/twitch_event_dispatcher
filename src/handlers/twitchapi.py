import os
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

from dispatcher.event_dispatcher import post_event


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
    async def runner():
        twapi = myTwitch()
        await twapi.get_user_id(user_name)
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

    def __init__(self):
        self.twapi_queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)
        self.scopes = TARGET_SCOPES
        #self.use_cli = use_cli
        #asyncio.create_task(self.twapi_task_runner())

    async def __aenter__(self):
        self.logger.debug("aenter")
        self.twitch, self.user = await self.get_twitch_api_conn()
        #asyncio.create_task(self.twapi_task_runner())
        
        return self
    async def init_sna(self):
        self.logger.debug("aenter")
        self.twitch, self.user = await self.get_twitch_api_conn()
        
    async def get_user_id(self, user_name: str):
        self.logger.debug(f"get_user_id: {user_name.get("user_name")}" )
        x  = await first(self.twitch.get_users(logins=[user_name.get("user_name")]))
        
        post_event("twapi_user_id_result", x.id)
        pass
    async def twapi_task_runner(self):
        try:
            self.logger.debug("twapi task_worker")
            #self.logger.debug(self)
            while True:
                self.logger.debug("TWAPI QUEUE")
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
               
        except Exception as e:
            self.logger.critical(f"TWAPI_TASK_RUNNER Exception: {e}", exc_info=True)

    def enqueue(self, coro):
        #self.logger.debug(self)
        self.logger.debug(f"~~~~~~~enqueued:{coro} {coro.__name__}")
        self.twapi_queue.put_nowait(coro)
        self.logger.debug(f"after put: twapi queue size: {self.twapi_queue.qsize()}")

    async def dispatch_twitch_event(self, event ):
        self.logger.debug("in dispatch_twitch_event")
        event_source = "twitch_event"
        ts = datetime.datetime.now()
        data = ""
        self.logger.debug(f'x: {type(x)}') #s
        if self.event_map[type(x)] != None:
            self.logger.debug(f"**** event_type:-----------------> >>> {x.subscription.type} <<<")
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
        self.logger.debug("send_chat_message?????")
        await self.twitch.send_chat_message(self.user.id, self.user.id, message)

    async def __aexit__(self, exc_type,exc_val, exc_tb):
        await self.twitch.close()

    async def auth_token_generator(self, twitch: Twitch, USER_SCOPE) -> (str, str):
        redirection_url ="http://localhost:17561"
        auth = UserAuthenticator(twitch, self.scopes,url=redirection_url,  host='0.0.0.0', port=17561)
        token, refresh_token = await auth.authenticate()

        return token, refresh_token

    async def get_twitch_api_conn(self) -> Tuple[ Twitch, TwitchUser]:
        #if self.use_cli:
        #load_dotenv("/home/sna/src/twitch/src/handlers/.env_twitchapi")
        load_dotenv("/home/sna/src/twitch/src/handlers/.env_twitchapi")
        await asyncio.sleep(1)
        client_id = os.getenv("CLIENT_ID", "ERROR_CLIENT_ID")
        self.logger.debug(f"client_id: {client_id}")
        client_s = os.getenv("CLIENT_SECRET", "ERROR_CLIENT_SECRET")
        client_id = "0oyr3pfdb6p825pypylc4j5ymvpjzv"
        self.logger.debug(f"client_secret: {client_s}")
        auth_base_url = os.getenv("AUTH_BASE_URL", "ERROR_AUTH_BASE_URL")
        twitch = await Twitch(client_id,client_s )
        #helper = UserAuthenticationStorageHelper(twitch, self.scopes, storage_path="/home/sna/src/twitch-irc/auth_storage/snarequests.json")#/home/sna/src/twitch/auth_storage
        helper = UserAuthenticationStorageHelper(twitch, self.scopes, storage_path="/home/sna/src/twitch/auth_storage/snarequests.json", auth_generator_func=self.auth_token_generator)
        #helper = UserAuthenticationStorageHelper(twitch, self.scopes, url=auth_base_url, host="localhost", port=17561)
        await helper.bind()
        user = await first(twitch.get_users())
        self.logger.debug('{user.dict()}')

        return twitch, user

            
        
    async def get_followers(self):
        # MODERATOR_READ_FOLLOWERS
        logger.info("get followers????")
        result = await self.twitch.get_channel_followers(self.user.id)
        self.logger.info(f"total_followers: {result.total}")
        follower = []
        async for x in result:
            #self.logger.debug(x.to_dict())
            data =  {
                "followed_at"   : x.followed_at,
                "user_id"       : x.user_id,
                "user_name"     : x.user_name,
                "user_login"    : x.user_login
            }
            #self.logger.debug(data)
            db_handler.insert_new_follwer(data)
            follower.append(data)
            #self.logger.debug(follower)
        return follower
    
    async def get_follower_count(self):
        result = await self.twitch.get_channel_followers(self.user.id)
        await self.get_followers()
        data = { "event_type" : "follower_count", 
                "event_data" : {"total_follower": result.total} }
        self.logger.info(f"xx total_followers: {result.total}")
        post_event("twitchapi_follower_counter", data)
        

    async def create_clip(self):
        clip = await self.twitch.create_clip(self.user.id)
        async for x in clip:
            print (x)

    async def get_current_subscribers(self):
        subscribers = await self.twitch.get_broadcaster_subscriptions(self.user.id)
        self.logger.info (f"subcount:  {subscribers.total}")
        async for x in subscribers:
            self.logger.debug(f"subs: {x.user_name}")

        """
        await self.twitch.add_channel_vip(broadcaster_id=self.user.id, user_id=1287837934)
        await self.twitch.remove_channel_vip(broadcaster_id=self.user.id, user_id=1287837934)
        await self.twitch.add_channel_vip(broadcaster_id=self.user.id, user_id=1287837934)
        await self.twitch.remove_channel_vip(broadcaster_id=self.user.id, user_id=1287837934)
        await self.twitch.add_channel_vip(broadcaster_id=self.user.id, user_id=1287837934)
        await self.twitch.remove_channel_vip(broadcaster_id=self.user.id, user_id=1287837934)
        """
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
        self.logger.info(f"xx total_subs: {subscribers.total}")
        post_event("twitchapi_sub_count", data)

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
                 AuthScope.USER_WRITE_CHAT
                 ]
