from twitchAPI.twitch import Twitch, TwitchUser
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat.middleware import StreamerOnly
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand,JoinEvent,LeftEvent, MessageDeletedEvent, NoticeEvent#, RAID, MESSAGE_DELETE, NOTICE
from twitchAPI.object.api import TwitchUser
from pathlib import PurePath
from twitchAPI.helper import first
import sys
import logging
import asyncio
from dotenv import load_dotenv

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
    
load_dotenv(dotenv_path="/home/sna/src/twitch/src/events/.env_twitch_irc", verbose=True)
chat_client = None
twitch = None

def logger(msg):
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(f'{datetime.datetime.now().strftime( "%H:%M" )}')
        logger.info(str(msg))

async def auth_token_generator(twitch: Twitch, USER_SCOPE) -> (str, str):
    
    auth = UserAuthenticator(   twitch, 
                                USER_SCOPE,
                                url=os.getenv("IRC_BOT_OAUTH_REDIRECTION_URI"),  
                                host='0.0.0.0', 
                                port=os.getenv("IRC_BOT_OAUTH_PORT"))
    token, refresh_token = await auth.authenticate()

    return token, refresh_token

async def unify_chat_command(cmd: ChatCommand):
    return "unified_chat_command"

async def unify_chat_event(chatevent: ChatEvent):
    logger.debug(type(chatevent))
    return "unified_chat_event"

async def on_command(cmd: ChatCommand):
    unified_chat_command = unify_chat_command(cmd)
    #dispatch

async def on_chat_event(chatevent: ChatEvent):
    unified_chat_event = unify_chat_event
    type(chatevent) 
    #dispatch


def send_message():
    return "event created"

async def run():
    global twitch
    twitch = await Twitch(os.getenv("IRC_BOT_CLIENT_ID"), os.getenv("IRC_BOT_CLIENT_SECRET"))
    helper = UserAuthenticationStorageHelper(twitch, USER_SCOPE, storage_path=os.getenv("AUTH_STORAGE_FILE"))
    #helper = UserAuthenticationStorageHelper(twitch, USER_SCOPE, storage_path="/home/snafu/src/twitch-irc/auth_storage/snabotski.json", auth_generator_func=auth_token_generator)
    await helper.bind()
    chat = await Chat(twitch)
    await chatlog_init()

    chat.register_event(ChatEvent.READY, on_chat_event)
    chat.register_event(ChatEvent.MESSAGE, on_chat_event)
    chat.register_event(ChatEvent.SUB, on_chat_event)
    chat.register_event(ChatEvent.READY, on_chat_event)
    chat.register_event(ChatEvent.JOINED, on_chat_event) # bot join
    chat.register_event(ChatEvent.JOIN, on_chat_event)
    chat.register_event(ChatEvent.LEFT, on_chat_event)
    chat.register_event(ChatEvent.USER_LEFT, on_chat_event)
    chat.register_event(ChatEvent.RAID, on_chat_event)
    chat.register_event(ChatEvent.MESSAGE_DELETE, on_chat_event)
    chat.register_event(ChatEvent.NOTICE, on_chat_event)

    
    chat.register_command('sb', on_command)
    chat.register_command('sbusers', on_command)
    chat.register_command('dc', on_command)
    chat.register_command('git', on_command)
    chat.register_command('sna', on_command)
    chat.register_command('today', on_command)
    chat.register_command("snaman", on_command)
    chat.register_command('bait', on_command)
    chat.register_command('topbait', on_command)
    chat.register_command('mytopbait', on_command)
    chat.register_command("slap", on_command)
    chat.register_command("dynamite", on_command)
    chat.register_command("stats", on_command)
    chat.register_command("who", on_command)

    chat.start()

    global chat_client
    chat_client = chat

    try:
        while True:
            time.sleep(0.1)
        #on_test()
    except Exception as e:
        logger.debug(e)
    finally:
        chat.stop()
        await twitch.close()

asyncio.run(run())