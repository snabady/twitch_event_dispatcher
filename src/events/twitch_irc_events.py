import subprocess
import threading
from functools import partial
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
import logging
from utils import log
from dispatcher.event_dispatcher import post_event, subscribe_event
from handlers import db_handler, stream_stats
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
logger.setLevel(logging.INFO)   

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Irc(metaclass=Singleton):

    def __init__(self):
        self.logger             = logging.getLogger("IRC_BOT")
        if not self.logger.hasHandlers():
            log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)   
        self.twitch             = None
        self.chat_client        = None
        self.twitch             = None
        self.user_id            = None
        self.broadcaster_id     = None
        self.irc_queue          = asyncio.Queue()
        self.cmd_list           = db_handler.get_chat_commands()
        self.stream_online      = False
        subscribe_event("set_stream_online", self.set_stream_online)
        subscribe_event("irc_send_message", self.trigger_sendmessage)
        subscribe_event("trigger_send_message", self.trigger_sendmessage)
        self.auto_commands = self.create_auto_command_list()
        self.loop               = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start() 
        self.client_id          = None
        self.client_secret      = None
        self.client_name        = None
        self.target_channel     = None
        self.redirection_url    = None
        self.oauth_port         = None 
        self.oauth_host         = None
        self.auth_storage_file  = None
        self.load_dotenv_variables()
        self.last_now_playing = ""
        self.current_vips = None
        self.stream_stats_data = stream_stats.ChatStats()


    def set_stream_online(self, event_data):
        self.logger.debug("set_stream_online data {event_data.get('event_data')}")
        value = event_data.get("event_data")
        self.stream_online = value
    
    def load_dotenv_variables(self):
        self.client_name        = os.getenv("IRC_BOT_USERNAME", "could not get IRC_BOT_USERNAME os.getenv()")
        self.client_id          = os.getenv("IRC_BOT_CLIENT_ID", "could not get IRC_BOT_client_id os.getenv()")
        self.client_secret      = os.getenv("IRC_BOT_CLIENT_SECRET", "could not get client secret os.getenv()")
        self.target_channel     = os.getenv("IRC_BOT_CHANNEL_JOIN", "could not get target_channel os.getenv()")
        self.redirection_url    = os.getenv("IRC_BOT_OAUTH_REDIRECTION_URI", "could not get Iredirection uri os.getenv()")
        self.oauth_port         = os.getenv("IRC_BOT_OAUTH_PORT", "could not get port os.getenv()")
        self.oauth_host         = os.getenv("IRC_BOT_OAUTH_HOST", "could not get host os.getenv()")
        self.auth_storage_file  = os.getenv("IRC_BOT_AUTH_STORAGE_FILE", "could not get auth_storage_file os.getenv()")
        self.logger.debug(f"IRC_BOT_USERNAME: {self.client_name}")
    def create_auto_command_list(self):
        auto_commands = {}
        for x in self.cmd_list :
            if x[2] == 1:
                auto_commands[x[0]] = x[1]
        return auto_commands

    """ synchron irc_send_message_trigger """
    def trigger_sendmessage(self, msg):
        
        self.logger.debug("trigger_sendmessage")
        async def runner():
            self.logger.debug("hello from trigger_sendmessage runner ") 
            await self.send_chat_message(msg)
        asyncio.run_coroutine_threadsafe(runner(), self.loop)

    async def auth_token_generator(self,  twitch: Twitch, USER_SCOPE) -> (str, str):
        
        auth = UserAuthenticator(twitch, 
                                 USER_SCOPE,
                                 url=self.redirection_url,  
                                 host=self.oauth_host, 
                                 port=self.oauth_port)
        token, refresh_token = await auth.authenticate()

        return token, refresh_token

    async def getUser(self, str):
        x = [str]
        user = await first(self.twitch.get_users(logins=x))
        return  user.id

    async def send_chat_message(self, msg):
        await self.twitch.send_chat_message(self.broadcaster_id, self.user_id, msg)
       
    async def end_irc(self):
        self.chat.stop()
        await self.twitch.close()
    
    async def dispatch_event(self, event_type, event):
        self.logger.debug(f"dispatching: {event_type}")
        eventt={"irc_instance":self,
                "event_type": event_type,
                "event_data": event}
        
        if event_type == ChatEvent.JOINED:
            user_id = await self.getUser(self.target_channel)
#            await self.send_chat_message("o/")
            post_event("IRC_JOINED", eventt)
            
        elif event_type == "IRC_COMMAND":
            self.logger.debug(f"got irc cmd: {event}")
            post_event(event_type, eventt)
        elif event_type == ChatEvent.JOIN:
            post_event("IRC_JOIN", eventt)
        elif event_type == ChatEvent.MESSAGE:
            post_event("IRC_MESSAGE", eventt)
        elif event_type == ChatEvent.USER_LEFT:
            post_event("IRC_LEFT", eventt)

    async def now_playing(self):

        try:
            song = subprocess.check_output(["audtool", "current-song"], text=True).strip()
            if song != self.last_now_playing:
                msg=(f"now_playing: {song}")
                self.last_now_playing = song
                # TODO schalter einbaun
                #await self.send_chat_message(msg)
        except subprocess.CalledProcessError:
            pass

    async def run(self):
        self.twitch = await Twitch(self.client_id, self.client_secret) 
        helper = UserAuthenticationStorageHelper(self.twitch, USER_SCOPE, storage_path=self.auth_storage_file, auth_generator_func=self.auth_token_generator)
        await helper.bind()
        
        self.user_id = await self.getUser(self.client_name)
        self.broadcaster_id = await self.getUser(self.target_channel)

        self.chat = await Chat(self.twitch, initial_channel=[self.target_channel])

        self.chat.register_event(ChatEvent.READY, partial(self.dispatch_event, ChatEvent.READY) )
        self.chat.register_event(ChatEvent.MESSAGE, partial(self.dispatch_event, ChatEvent.MESSAGE))
        self.chat.register_event(ChatEvent.SUB, partial(self.dispatch_event, ChatEvent.SUB))
        self.chat.register_event(ChatEvent.JOINED, partial(self.dispatch_event, ChatEvent.JOINED) )
        self.chat.register_event(ChatEvent.JOIN, partial(self.dispatch_event, ChatEvent.JOIN))
        self.chat.register_event(ChatEvent.LEFT, partial(self.dispatch_event, ChatEvent.LEFT))
        self.chat.register_event(ChatEvent.USER_LEFT, partial(self.dispatch_event, ChatEvent.USER_LEFT))
        self.chat.register_event(ChatEvent.RAID, partial(self.dispatch_event, ChatEvent.RAID))
        self.chat.register_event(ChatEvent.MESSAGE_DELETE, partial (self.dispatch_event, ChatEvent.MESSAGE_DELETE))
        self.chat.register_event(ChatEvent.NOTICE, partial(self.dispatch_event, ChatEvent.NOTICE))

        for x in self.cmd_list:
            self.logger.debug(f"irc_command: {x[0]}, {x}")
            self.chat.register_command(x[0], partial(self.dispatch_event, "IRC_COMMAND"))
        self.current_vips = db_handler.execute_query("select user_name, user_id from special_users where is_vip = 1", None)
        self.chat.start()
        try:
            while True:
                await self.now_playing()
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            logger.debug("more graceful shit?")
            
        except Exception as e:
            self.logger.debug(e)
            self.logger.critical("RIP")
        finally:
            self.chat.stop()
            await self.twitch.close()

