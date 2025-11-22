from collections import defaultdict, Counter, OrderedDict
from datetime import datetime
import json
from twitchAPI.chat import ChatCommand, ChatMessage
import aiofiles
import logging
from src.utils import log
from src.handlers.db_handler import get_chat_commands ,get_stats_columns, insert_stream_stats

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   



class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ChatStats(metaclass=Singleton):

    db_cmd_list = get_chat_commands() 

    stats_history_map = get_stats_columns()

    def __init__(self):
        self.msg_per_user           = defaultdict(int)
        self.lettercount_per_user   = defaultdict(int)
        self.total_msg              = 0
        self.daily_msg              = 0
        self.stream_start_time      = None
        self.stream_end_time        = None
        self.cmd_cnt                = Counter()
        self.new_subs               = 0
        self.new_follower           = 0
        self.new_chatter            = 0
        self.ret_chatter            = 0
        self.channel_joins          = 0
        self.total_channel_joins    = 0
        self.first_message_cnt      = 1
        self.user_first_message_rank= defaultdict(int)
        self.unique_viewers         = OrderedDict()
        self.total_follower         = 0
        self.total_subs             = 0
        self.raids_received         = 0
        self.init_cmd_list()
#        logger.debug(f"-----------------------------__> self.cmd_list:  {self.cmd_list}")

    def process_msg(self, msg: ChatMessage):
        logger.debug(msg)
        msg_ = msg.text.split(" ")[0]

        if not msg.user.name == "snabotski" and msg_ not in self.cmd_list:
            if msg.user.name not in self.user_first_message_rank:
                self.user_first_message_rank[msg.user.name] = self.first_message_cnt
                self.first_message_cnt += 1
            self.daily_msg += 1
            self.msg_per_user[msg.user.name] += 1
            self.lettercount_per_user[msg.user.name]= len(msg.text)
            logger.debug(f"lettercount: {len(msg.text)}")
        self.cnt_cmd(msg)
    def add_raids_received():
        # TODO
        # add username / viewercount
        self.raids_received+=1
    def get_user_stats(self, user):
        return self.msg_per_user(user)
    def init_cmd_list(self):
        self.cmd_list = []
        
        for cmd in self.db_cmd_list:
            self.cmd_list.append("!"+cmd[0])
    # increase chat-command- counter
    def cnt_cmd(self, msg: ChatMessage):
        #logger.debug(self.cmd_list)
        for c_cmd in self.cmd_list:
            if msg.text.startswith(c_cmd):
                self.cmd_cnt[c_cmd] += 1

    def get_cmd_cnt(self, cmd):
        return self.cmd_cnt.get(cmd, -1)

    def get_stats_str(self):
        x= f'chatmessages: {self.daily_msg} '
        logger.debug(self.cmd_cnt.items())
        for command,cnt in self.cmd_cnt.items():
            logger.debug(command)
            x+=f'- {command}: {cnt}x'
            
        x += f" foo: {self.channel_joins}|{len(self.unique_viewers)} "
        #logger.debug(f" { for name, rank in  self.user_first_message_rank)
        logger.debug(f"{[(name, rank) for name, rank in self.user_first_message_rank.items()]}")
        return x
    
    def add_channel_join(self, user_name: str):
        if user_name not in self.unique_viewers:
            self.unique_viewers[user_name] = datetime.now()
        #print(f"unique_viewers: {self.unique_viewers}")  
        self.channel_joins += 1

    
    def print_unique_viewers(self):
        #print(f"unique_viewers: {self.unique_viewers}")  
        for user, time in self.unique_viewers.items():
            print(f"{user}: {time}")


    def get_view_count(self):
        return len(self.unique_viewers)

    def write_stats_history_to_db(self):
        db_values = [datetime.now(), 
                     self.total_msg, 
                     self.new_subs, 
                     self.new_follower,
                     self.new_chatter,
                     self.channel_joins,
                     self.first_message,
                     len(self.unique_viewers),
                     self.total_channel_joins,
                     self.daily_msg,
                     self.total_subs,
                     self.total_follower,
                     self.raids_received]
        insert_stream_stats(db_values)
            

    def init_stats(self):
        raise NotImplementedError          

def handle_twitch_streaminfo_event(event: dict):
    fn = event.get("event_type")
    fn(event)

def handle_stream_online(event: dict):
    logger.debug("handle_stream_online")
    event_data = event.get("event_data")
    started_at              = event.get("started_at")
    
    logger.debug("WE DID IT ")

    #stream_stats_data.stream_start_time = started_at


def handle_stream_offline(event: dict):
    logger.debug("handle_stream_offline")
    event_data = event.get("event_data")
    logger.debug(f"event_data: {event_data}")
    
    

    #stream_stats_data.stream_start_time = started_at


def handle_channel_update_v2(event: dict):
    logger.debug("handle_channel_update_v2")

def handle_channel_udpate(event: dict):
    logger.debug("handle_channel_update")
