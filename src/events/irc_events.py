from twitchAPI.twitch import Twitch, TwitchUser
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat.middleware import StreamerOnly
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand,JoinEvent, JoinedEvent,LeftEvent, MessageDeletedEvent, NoticeEvent#, RAID, MESSAGE_DELETE, NOTICE
from twitchAPI.object.api import TwitchUser
from pathlib import PurePath
from twitchAPI.helper import first
import sys
import os
import logging
import asyncio
from dotenv import load_dotenv
import logging
from utils import log
from dispatcher.event_dispatcher import post_event, subscribe_event

from handlers import db_handler
import time

USER_SCOPE = [
    AuthScope.CHAT_READ, 
    AuthScope.CHAT_EDIT,
    AuthScope.CHANNEL_MODERATE,
    AuthScope.USER_READ_EMAIL,
    AuthScope.MODERATOR_READ_FOLLOWERS,
    AuthScope.CHANNEL_MANAGE_POLLS,
    AuthScope.CHANNEL_BOT,
    AuthScope.USER_BOT,
    AuthScope.USER_WRITE_CHAT
    ]


logger = logging.getLogger(__name__)
log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        #cls._instances[cls] = super(Singleton, cls).__call__(*args,**kwargs)
        #return cls._instances[cls]
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Irc(metaclass=Singleton):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            self.log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)   
        self.twitch = None
        self.chat_client = None
        self.twitch = None
        self.user_id = None
        self.broadcaster_id = None
        self.irc_queue = asyncio.Queue()
        self.cmd_list = db_handler.get_chat_commands()
        self.stream_online = False
        

        subscribe_event("irc_send_message", self.trigger_send_message)
        subscribe_event("set_stream_online", self.set_stream_online)


    def set_stream_online(self, event_data):
        value = event_data.get("event_data")
        self.stream_online = value

    async def auth_token_generator(self,  twitch: Twitch, USER_SCOPE) -> (str, str):
        redirection_url ="http://localhost:17559"
        auth = UserAuthenticator(twitch, USER_SCOPE,url=redirection_url,  host='0.0.0.0', port=17559)
        token, refresh_token = await auth.authenticate()

        return token, refresh_token

    """async def auth_token_generator(twitch: Twitch, USER_SCOPE) -> (str, str):
        logger.debug(f"AUTH_TOKEN_GENERATOR_OAUTH_URI: {os.getenv("IRC_BOT_OAUTH_REDIRECTION_URI")}")
        auth = UserAuthenticator(   twitch, 
                                    USER_SCOPE,
                                    url=os.getenv("IRC_BOT_OAUTH_REDIRECTION_URI"),  
                                    host='0.0.0.0', 
                                    port=os.getenv("IRC_BOT_OAUTH_PORT"))
        token, refresh_token = await auth.authenticate()
        logger.debug(f"token {token} re.fresh_token {refresh_token}")
        return token, refresh_token""" 

    async def unify_chat_command(self, cmd: ChatCommand):

        return {"cmd_name" : cmd.name, "cmd_params": cmd.parameter}

    async def unify_chat_event(self, chatevent: ChatEvent):
        self.logger.debug(chatevent)
        if not type(chatevent) == ChatEvent.MESSAGE: 
            unified_chat_command = {
                "blub":chatevent

            }
            post_event("irc_chat_event", unified_chat_command)
        else: 
            self.logger.debug("this was a chatmessage and no error")

    async def on_command(self, cmd: ChatCommand):
        self.logger.debug("jolooooo")  
        self.logger.debug(f"cmd.name: {cmd.name}")
        if cmd.name =="bait":
            
            logger.debug("ajo it is a bait")
            post_event("fish_bait",cmd.user.display_name)
        if cmd.name == "mytopbait":
            post_event("mytopbait_command", {"event_type": "mytopbait_command", 
                                            "event_data": cmd.user.display_name})
        elif cmd.name =="topbait":
            post_event("topbait_command", { "event_type": "topbait_command", 
                                            "event_data": cmd.user.display_name})
        elif cmd.name  =="followage":
            self.logger.debug("followage_command triggered")
            
            post_event("db_get_followage_by_user", {"user_name": cmd.user.display_name})

    async def on_joined(self, chatevent: JoinedEvent):
        event_type = type(chatevent)     
        if isinstance(chatevent, JoinedEvent):
            joined_vent : JoinedEvent = chatevent
            self.logger.debug(f"#{joined_vent.user_name}# just joined ")

    async def on_ready(self, event: EventData):
        self.logger.debug("on ready")
        
        
        await event.chat.join_room(os.getenv("IRC_BOT_CHANNEL_JOIN"))
        
        self.broadcaster_id = await self.getUser("5n4fu")
        self.user_id = await self.getUser("snabotski")

    async def on_chat_msg(self, msg: ChatMessage):
        if (msg.text).find("FLASH")>-1:
            post_event("snafu_flash_event", {"user_name": msg.user.id})

    async def getUser(self, str):
        x = [str]
        user = await first(self.twitch.get_users(logins=x))
        return  user.id

    def trigger_send_message(self, msg):
        """ async def runner():
            
            await send_chat_message(msg)
        asyncio.create_task(runner())
        """
        self.irc_queue.put_nowait(self.send_chat_message(msg))
    async def send_chat_message(self, msg):
        
        await self.twitch.send_chat_message(self.broadcaster_id, self.user_id, msg)

    async def on_chat_event(self, event: EventData):
        
        self.logger.debug(f"received Event type: {type(event)}")

        if isinstance(event, JoinEvent):
            self.logger.info(f"User '{event.user_name}' joined ")
        elif isinstance(event, LeftEvent):
            self.logger.info(f"User '{event.user_name}' left")
        elif isinstance(event, ChatMessage):
            self.logger.info(f"Message from '{event.user.name}': {event.text}")
        elif isinstance(event, ChatSub):
            self.logger.info(f"Sub from '{event.user.name}' in {event.room}")
        elif isinstance(event, MessageDeletedEvent):
            self.logger.info(f"Message deleted in {event._name}")
        elif isinstance(event, NoticeEvent):
            self.logger.info(f"Notice in {event._name}: {event.message}")
    
        post_event("irc_chat_event", event)


    async def irc_task_runner(self):
        try:
            self.logger.debug("IRC task worker")
            
            while True:
                self.logger.debug("IRC QUEUE")
                #if self.obs_task_queue.qsize() > 0:
                task_coro_func = await self.irc_queue.get()
                                
                try:
                    self.logger.debug("irc_task_runner executing")
                    await task_coro_func# Execute the coroutine
                except Exception as e:
                    self.logger.critical(f"IRC_RUNNER Exception: {e}", exc_info=True)      
                finally:
                    self.irc_queue.task_done()   
                    self.logger.debug(f"IRC_QUEUE-size: {self.irc_queue.qsize()}")
                
        except Exception as e:
            self.logger.critical(f"IRC_TASK_RUNNER Exception: {e}", exc_info=True)

    def enqueue(self, coro):
        #self.logger.debug(self)
        self.logger.debug(f"~~~~~~~enqueued:{coro} {coro.__name__}")
        irc_queue.put_nowait(coro)
        self.logger.debug(f"after put:IRIC queue size: {irc_queue.qsize()}")


    async def run(self):

        self.logger.debug("helloooo?")
        load_dotenv(dotenv_path="/home/sna/src/twitch/src/events/.env_twitch_irc", verbose=True)
        
        self.twitch = await Twitch(os.getenv("IRC_BOT_CLIENT_ID"), os.getenv("ICR_BOT_CLIENT_SECRET"))
        #helper = UserAuthenticationStorageHelper(twitch, USER_SCOPE, storage_path=os.getenv("AUTH_STORAGE_FILE"))
        helper = UserAuthenticationStorageHelper(self.twitch, USER_SCOPE, storage_path="/home/sna/src/twitch/auth_storage/snabotski.json", auth_generator_func=self.auth_token_generator)
        await helper.bind()
        self.chat = await Chat(self.twitch)
        #await chatlog_init()

        self.chat.register_event(ChatEvent.READY, self.on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self.on_chat_msg)
        self.chat.register_event(ChatEvent.SUB, self.on_chat_event)
        self.chat.register_event(ChatEvent.READY, self.on_chat_event)
        self.chat.register_event(ChatEvent.JOINED, self.on_joined) # bot join
        self.chat.register_event(ChatEvent.JOIN, self.on_chat_event)
        self.chat.register_event(ChatEvent.LEFT, self.on_chat_event)
        self.chat.register_event(ChatEvent.USER_LEFT, self.on_chat_event)
        self.chat.register_event(ChatEvent.RAID, self.on_chat_event)
        self.chat.register_event(ChatEvent.MESSAGE_DELETE, self.on_chat_event)
        self.chat.register_event(ChatEvent.NOTICE, self.on_chat_event)


        for x in self.cmd_list:
            self.logger.debug(f"irc_command: {x[0]}")
            self.chat.register_command(x[0], self.on_command)
        
        self.chat.start()


        try:
            self.logger.debug("tell me i am running thx")
            while True:
                await asyncio.sleep(0.1)
            #on_test()
        except Exception as e:
            self.logger.debug(e)
            self.logger.critical("RIP")
        finally:
            self.chat.stop()
            await self.twitch.close()

