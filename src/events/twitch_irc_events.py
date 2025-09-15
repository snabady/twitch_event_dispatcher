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

# screenkey -f "Monaspace Krypton" --font-color cyan -s large -M --geometry 800x200+100+300  --window &
logger = logging.getLogger(__name__)
log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
loop = asyncio.new_event_loop()
t = threading.Thread(target=loop.run_forever, daemon=True)
t.start()
class Irc(metaclass=Singleton):

    def __init__(self, dotenv_path):
        self.dotenv_path = dotenv_path
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
        self.TARGET_CHANNEL =["5n4fu"]
        self.auto_commands = self.create_auto_command_list()
        
    def set_stream_online(self, event_data):
        self.logger.debug("set_stream_online data {event_data.get('event_data')}")
        value = event_data.get("event_data")
        self.stream_online = value
         
    def create_auto_command_list(self):
        auto_commands = {}
        for x in self.cmd_list :
            if x[2] == 1:
                auto_commands[x[0]] = x[1]
        return auto_commands
    async def auth_token_generator(self,  twitch: Twitch, USER_SCOPE) -> (str, str):
        redirection_url ="http://localhost:17563"
        auth = UserAuthenticator(twitch, USER_SCOPE,url=redirection_url,  host='0.0.0.0', port=17563)
        token, refresh_token = await auth.authenticate()

        return token, refresh_token
    
    def trigger_send_message(self, msg):
        
        self.logger.debug("blub... trigger.. send_message") 

 
        asyncio.run_coroutine_threadsafe(self.send_chat_message( msg), loop)

    async def getUser(self, str):
        x = [str]
        user = await first(self.twitch.get_users(logins=x))
        return  user.id

    async def send_chat_message(self, msg):
        user_id = await self.getUser("snatests")
        broadcaster_id = await self.getUser("5n4fu")
        await self.twitch.send_chat_message(broadcaster_id, user_id, msg)
       
    async def end_irc(self):
        self.chat.stop()
        await self.twitch.close()
    
    async def dispatch_event(self, event_type, event):
        self.logger.debug(f"dispatching: {event_type}")
        eventt={"irc_instance":self,
                "event_type": event_type,
                "event_data": event}
        
        if event_type == ChatEvent.JOINED:
            user_id = await self.getUser("5n4fu")
            await self.send_chat_message("o/")
            post_event("IRC_JOINED", eventt)
            
        elif event_type == "IRC_COMMAND":
            self.logger.debug(f"got irc cmd: {event}")
            post_event(event_type, eventt)
        elif event_type == ChatEvent.JOIN:
            post_event("IRC_JOIN", eventt)
        elif event_type == ChatEvent.MESSAGE:
            post_event("IRC_MESSAGE", eventt)


    async def run(self):

        load_dotenv(dotenv_path=self.dotenv_path, verbose=True)
        self.twitch = await Twitch(os.getenv("IRC_BOT_CLIENT_ID"), os.getenv("ICR_BOT_CLIENT_SECRET"))
        helper = UserAuthenticationStorageHelper(self.twitch, USER_SCOPE, storage_path=os.getenv("AUTH_STORAGE_FILE"))
        #helper = UserAuthenticationStorageHelper(self.twitch, USER_SCOPE, storage_path="/home/sna/src/twitch/auth_storage/snatests.json", auth_generator_func=self.auth_token_generator)
        await helper.bind()
        self.chat = await Chat(self.twitch, initial_channel=self.TARGET_CHANNEL)

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
        
        self.chat.start()
        
        try:
            while True:
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            logger.debug("more graceful shit?")
            
        except Exception as e:
            self.logger.debug(e)
            self.logger.critical("RIP")
        finally:
            self.chat.stop()
            await self.twitch.close()

