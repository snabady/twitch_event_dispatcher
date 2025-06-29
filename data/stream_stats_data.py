from collections import defaultdict, Counter, OrderedDict
from datetime import datetime
import json
from twitchAPI.chat import ChatCommand, ChatMessage
import asyncio
import aiofiles
import scripte.async_file_io as as_file_io

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        #cls._instances[cls] = super(Singleton, cls).__call__(*args,**kwargs)
        #return cls._instances[cls]
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]



class ChatStats(metaclass=Singleton):

    stats_history_file = f'/home/sna/src/scripte_twitch/data_files/stats/stats_history.csv'

    cmd_list = ["!bait",
                "!topbait",
                "!mytopbait",
                "!git",
                "snaman",
                "!sb",
                "!sbusers",
                "!dynamite",
                "!slap",
                "!sna",
                "!stats",
                "!today",
                "!stats", 
                "!stalk",
                "!test",
                "!end"]
    
    stats_history_map = {
        'date'    :             0,
        'total_msg':            1,
        'new_subs':             2,
        'new_follower':         3,
        'new_chatter':          4,
        'channel_joins':        5,
        'first_msgs':           6,
        'unique_viewer_cnt':    7,
        'total_channel_joins':  8,
        'daily_msg':            9,
        'total_subs':           10,
        'total_follower':       11
    }


    def __init__(self):
        self.msg_per_user           = defaultdict(int)
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
        self.first_message          = 0
        self.unique_viewers         = OrderedDict()
        self.total_follower         = 0
        self.total_subs             = 0

        self.stats_hist_io = as_file_io.AsyncFileIO(self.stats_history_file)

    def process_msg(self, msg: ChatMessage):
        msg_ = msg.text.split(" ")[0]
        if not msg.user.name == "snabotski" and msg_ not in self.cmd_list:
            self.daily_msg += 1
            self.msg_per_user[msg.user.name] += 1
        await self.cnt_cmd(msg)

    def get_user_stats(self, user):
        return self.msg_per_user(user)

    def cnt_cmd(self, msg: ChatMessage):
        for c_cmd in self.cmd_list:
            if msg.text.startswith(c_cmd):
                self.cmd_cnt[c_cmd] += 1

    def get_cmd_cnt(self, cmd):
        return self.cmd_cnt.get(cmd, -1)

    def get_stats_str(self):
        x= f'chatmessages: {self.daily_msg} '
        for command,cnt in self.cmd_cnt.items():
            x+=f'- {command}: {cnt}x'
        x += f" foo: {self.channel_joins}|{len(self.unique_viewers)} "
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

    def write_stats_history(self):
        self.total_subs+= self.new_subs 
        self.total_follower += self.new_follower
        self.total_channel_joins += len(self.unique_viewers)
        
        self.total_msg += self.daily_msg
        date = datetime.now()
        line = f'{date};{self.total_msg};{self.new_subs};{self.new_follower};{self.new_chatter};{self.channel_joins};{self.first_message};{len(self.unique_viewers)};{self.total_channel_joins};{self.daily_msg};{self.total_subs};{self.total_follower}'
        await self.stats_hist_io.write_snafu_stats_history(line)
    
    def init_stats(self):
        
        lastline = await self.stats_hist_io.read_last_line()
        lastline = lastline.split(";")
        print(type(lastline[self.stats_history_map['total_msg']]))
        print(lastline[self.stats_history_map['total_msg']])
        self.total_msg              = int(lastline[self.stats_history_map['total_msg']])
        self.total_channel_joins    = int(lastline[self.stats_history_map['total_channel_joins']])
        self.total_follower         = int(lastline[self.stats_history_map['total_follower']])
        self.total_subs             = int(lastline[self.stats_history_map['total_subs']])


    


            
                


