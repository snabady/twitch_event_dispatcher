from twitchAPI.chat import ChatCommand
import asyncio
import os
import time
import random 
import aiofiles
from obs_websocket import my_obsws
import logging
import colorlog
from dotenv import load_dotenv

class Bait():

    def __init__(self, fish_list, topDisplay):

        self.logger = logging.getLogger(__name__)
        self.add_logger_handler()
        self.logger.setLevel(logging.DEBUG)
        

        self.fish_list  = fish_list
        self.topDisplay = topDisplay
        self.zonks      = ["⚓", "🚲", "🥠", "🧦", "✂"]
        self.fishis     = ["🐟", "🐠", "🐡", "🍥", "🦞" , "🦐"]
        self.baitcount  = 0
        self.obsws = my_obsws.Obs_ws()
        self.max_weight_regular = 756
        self.max_weight_dynamite = 999
        self.max_fishies = 166
        self.ascii_fishies=[]
        self.cnt_no_catches = 0
        self.cnt_catches = 0
        
        #ff52fc
        #4d194d
        #05ffff

        self.obs_file_lowbait   = "/home/sna/src/scripte_twitch/data_files/stats/lowbait.txt"
        self.obs_file_topbait   = "/home/sna/src/scripte_twitch/data_files/stats/topbait.txt"
        self.obs_file_bait      = "/home/sna/src/scripte_twitch/data_files/baits.txt"
        self.slap_path          = "/home/sna/mp3/slaps/"
        self.obs_file_fishing_slot_obs = "/home/sna/src/twitch-irc/obs_websocket/fishers/{fishing_slot_obs}.txt"
        self.v_formats = ('.mkv','.webm', '.mp4')

        self._lock      = asyncio.Lock()

    def __aenter__(self, exc_type, exc_value,traceback):
        print("__aenter__")
        
    
    async def init(self):
        print("init fish_game")
        self.ascii_fishies = await self.init_fish_population()
        await self.obsws.init()
        #await self.obsws.init_obswebsocket_ws()
        print("init obs ws done")
    
    async def init_fish_population(self):
        print("setting fishie population")
        self.ascii_fishies = {1,self.max_weight_regular-1}
        
        while len(self.ascii_fishies) < self.max_fishies-1:
            self.ascii_fishies.add(random.randint(1,self.max_weight_regular))
        
        self.ascii_fishies = list(self.ascii_fishies)
        random.shuffle(self.ascii_fishies)
        
        return self.ascii_fishies

    def add_logger_handler(self):
        handler = colorlog.StreamHandler()
        formatter = colorlog.ColoredFormatter(
            '%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def monitor_queue(self):
        while True:
            queue = await self.fish_list.get_queue()
            available_positions = await self.fish_list.get_available_positions()

            if available_positions and queue:
                cmd = queue[0]  
                await self.on_bait(cmd) 
                print(f"🎣-{cmd.user.name} next in queue")

            await asyncio.sleep(1) 

    async def ranking_fish(self, cmd: ChatCommand,gramm):
        top = await self.fish_list.is_top_bait(gramm)
        low = await self.fish_list.is_low_bait(gramm)
        fst = await self.fish_list.is_first_catch(gramm)
        #print(f'top, low, fst: {top,low,fst}')
        if top and gramm != -1 :
            await cmd.reply(f"!highscore bäm GG {gramm}g")
            lock = asyncio.Lock()
            async with lock:
                file = "/home/sna/src/scripte_twitch/data_files/stats/bait_highscore_user.txt"
                async with aiofiles.open(file, "w") as f:
                    await f.write(f"{cmd.user.display_name}")
            
            #quick and dirty before REEEEEEfactor
            self.obs_file_bait
            scene_item_id = await self.obsws.get_scene_item_id("fishers","bait_highscore_user")
            self.logger.debug(f"scene_item_id:\t{scene_item_id}")
            await self.obsws.set_source_visibility("fishers", scene_item_id, True)
            time.sleep(7)
            await self.obsws.set_source_visibility("fishers", scene_item_id, False)
            
            
        elif  low and gramm  != -1:
            await cmd.reply(f"!bonk lowballer catch OTD {gramm}g")
            

        elif fst and gramm != -1:
            await cmd.reply(f"first catch today!")

        return top,low,fst

    async def fish_a_fish_old(self, maxgramm, chance):
        if chance == 1:
            gramm = random.randint(1, maxgramm)
            fish = random.choice(self.fishis)
            return gramm, fish
        elif random.choice([True,False]) < chance:
            gramm = random.randint(1,maxgramm)
            fish = random.choice(self.fishis)
            return gramm, fish
        else: 
            loser = await self.fish_loser()
            return -1, loser

    async def fish_a_fish(self, maxgramm, chance):
        if  self.baitcount == 50:
            self.ascii_fishies.append(self.max_weight_regular)
            
        if len(self.ascii_fishies) > 0:
            
            gramm = self.ascii_fishies.pop(random.randrange(len(self.ascii_fishies)))
            is_a_catch = random.choice([True,False])

            #print(f"is a catch? {is_a_catch}")
            if is_a_catch:
                self.cnt_catches+=1
                return gramm, random.choice(self.fishis)
            else:
                self.cnt_no_catches+=1
                self.ascii_fishies.append(gramm)
                return -1, await self.fish_loser()
        return -1, await self.fish_loser()

    async def fish_loser(self):
        loser=random.choice(self.zonks)
        return loser

    async def update_fishing_list(self, user_name, gramm):
        self.topDisplay.set_bait(user_name, gramm)
        #await self.topDisplay.generate_file()
        lock = asyncio.Lock()
        async with aiofiles.open(self.obs_file_lowbait, "w") as f:
                await f.write(f"{user_name}: {gramm}g")

    async def update_low_catch(self,user_name, gramm):
        lock = asyncio.Lock()
        if gramm == -1:
            return
        async with aiofiles.open(self.obs_file_topbait, "w") as f:
                await f.write(f"{user_name}: {gramm}g")

    async def on_bait(self, cmd: ChatCommand):
        #
        # self.obsws
        #print(str(cmd.parameter))
        if self.obsws.is_online:

            fishing_slot_obs, free_slot_obs = await self.fish_list.get_fishing_slot_obs(cmd)
        else:
            fishing_slot_obs, free_slot_obs = await self.fish_list.get_fishing_slot(cmd)
        
        #if fishing_slot_obs == "queue":
            #print(f'added {cmd.user.name} to queue: {free_slot_obs}')
            #await cmd.reply(f"[{self.baitcount}]: all fishing slots are busy u are currently pos: {free_slot_obs}")
            return
        fisher_name = cmd.user.name
        
        # Lock für baitcount schreiben
        lock = asyncio.Lock()
        async with lock:
            self.baitcount += 1
            file = self.obs_file_bait
            async with aiofiles.open(file, "w") as f:
                await f.write(f"{self.baitcount}/50")
        async with lock:
            #file = self.obs_file_fishing_slot_obs.replace("{fishing_slot_obs}", fishing_slot_obs)
            file = f"/home/sna/src/twitch-irc/obs_websocket/fishers/{fishing_slot_obs}.txt"
            async with aiofiles.open(file, 'w') as f:
                x = f'{fisher_name}'
                await f.write(x)

        await cmd.reply(f"fishing got your bait")

        
        #fishing_slot_obs, free_slot_obs = await self.fish_list.get_fishing_slot_obs(cmd)
        #print(f'free_slot_obs: {free_slot_obs}')
        #print(f'fishing_slot_obs: {fishing_slot_obs}')
        if self.obsws.is_online:
            await self.obsws.init_obswebsocket_ws()
            #connected = await self.obsws.ws.connect()
            #if connected:
            slot_id = await self.obsws.get_scene_item_id("fishers", fishing_slot_obs)
            
            await self.obsws.set_source_visibility("fishers", slot_id, True)
        
   
        fishing_time = random.randint(6, 60)
        #await asyncio.gather(
        #    asyncio.sleep(fishing_time),
        #    self.run_xcow_pos(cmd.user.name, fishing_time, fishing_slot)
        #)
        await asyncio.sleep(fishing_time)
        if self.obsws.is_online:
            await self.obsws.set_source_visibility("fishers", slot_id, False)
        

        async with lock:
            file = f"/home/sna/src/twitch-irc/obs_websocket/fishers/{fishing_slot_obs}.txt"
            async with aiofiles.open(file, 'w') as f:
                await f.write("")

        gramm, fish = await self.fish_a_fish(self.max_weight_regular, 0.5)
        await self.fish_list.free_fishing_slot(free_slot_obs, cmd)
        if gramm == self.max_weight_regular:
            await cmd.reply("!alarm !highscore FISHIES u are now !VIP baiter! welcome to VIPCHAT")
            lock = asyncio.Lock()
            async with lock:
                file = "/home/sna/src/scripte_twitch/data_files/stats/bait_vip.txt"
                async with aiofiles.open(file, "w") as f:
                    await f.write(f"NEW VIP: {cmd.user.display_name}")
            
            # quick and dirty before REEEEEEfactor
            
            scene_item_id = await self.obsws.get_scene_item_id("fishers","bait_VIP")
            #self.logger.debug(f"scene_item_id:\t{scene_item_id}")
            await self.obsws.set_source_visibility("fishers", scene_item_id, True)
            time.sleep(30)
            await self.obsws.set_source_visibility("fishers", scene_item_id, False)

            


        if gramm != -1:
            await cmd.reply(f"u caught a <><  [{gramm}g|{fishing_time}s] 👀")
        else:
            await cmd.reply(f"jeBaited you've got {fish} FishingeDespair")

        top, low, fst = await self.ranking_fish(cmd, gramm)
        #print (f'{top} top {low} low {fst} fst')
        if top:
            await self.update_fishing_list(cmd.user.name, gramm)
        elif low:
            #print ("its low catch")
            await self.update_low_catch(cmd.user.name, gramm)
        if gramm > 0:
            await self.fish_list.add_catch(cmd.user.name, gramm)
        print(f"[{len(self.ascii_fishies)}] | [{self.baitcount}](-{self.cnt_no_catches}|+{self.cnt_catches}) --> {cmd.user.display_name} [{gramm}g|{fishing_time}] TOP? {top}")

    async def run_xcow_pos(self, msg, fishing_time, fishing_slot):
        ti  = f"--time={fishing_time}"
        img = f"--image=/home/snafu/src/scripte_twitch/img/pixel.png"
        pos = f"--at={fishing_slot},0"
        process = await asyncio.create_subprocess_exec(
            "xcowsay", msg, "--monitor=0", "--font=mono12", "--no-wrap", ti,img,pos
        )

    async def on_dynamite(self, cmd: ChatCommand):
        res = [
            await self.fish_a_fish( self.max_weight_dynamite, 1),
            await self.fish_a_fish( self.max_weight_dynamite, 0.5),
            await self.fish_a_fish( self.max_weight_dynamite, 0.5)
        ]
        await cmd.reply(str(res) + " work in progress")
        return res


    async def get_slap_video(self):

        videos =  await asyncio.to_thread(self.get_videos)
        
        if videos is not None:
            print("Randomly chosen slap video")
            return random.choice(videos)
        else:
            print("No slap videos found")
            return None

    def get_videos(self)        :
        all_files = os.listdir(self.slap_path)
        videos = [file for file in all_files if file.lower().endswith(self.v_formats)]
        return videos
