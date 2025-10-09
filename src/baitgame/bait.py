import math
import random
import logging
from utils import log
from queue import Queue
import threading
from dispatcher.event_dispatcher import post_event, subscribe_event
import time
from collections import defaultdict
from utils import file_io
from utils.file_io import write_bait_counter, bait_quotes_array
from events.obsws import set_source_visibility_wrapper
from handlers import db_handler 


MAX_SLOTS           = 18
USER_MAX_SLOTS      = 3


class RandomBaitSlotManager:
    def __init__(self, max_slots=18):
        self.max_slots = max_slots
        self.occupied = set()

    def get_free_slots(self):
        all_slots = [f"{i:02d}_bait" for i in range(1, self.max_slots + 1)]
        return [slot for slot in all_slots if slot not in self.occupied]

    def assign_slot(self):
        free = self.get_free_slots()
        if not free:
            return None  # Kein Slot frei
        slot = random.choice(free)
        self.occupied.add(slot)
        return slot

    def release_slot(self, slot):
        self.occupied.discard(slot)

    def get_occupied_slots(self):
        return list(self.occupied)



class FishSlotManager:
    def __init__(self, max_slots=MAX_SLOTS, user_max_slots=USER_MAX_SLOTS):
        self.max_slots = max_slots
        self.user_max_slots = user_max_slots
        self.active_slots = defaultdict(list)  # user -> [FishTask, ...]
        self.queue = Queue()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug("hello from FishSlotManager")

    def has_free_slot(self, user):
        # Prüfen, ob insgesamt noch ein Slot frei UND der User < user_max_slots hat
        active_count = sum(len(tasks) for tasks in self.active_slots.values())
        return (
            active_count < self.max_slots
            and len(self.active_slots[user]) < self.user_max_slots
        )

    def add_task(self, user, task):
        self.logger.debug(f"{user} starting {task}")
        if self.has_free_slot(user):
            self.active_slots[user].append(task)
            return True
        else:
            self.logger.debug(f"added {user} to queue")
            self.queue.put((user, task))
            return False

    def finish_task(self, user, task=None):
        # Optional: task kann übergeben werden, dann nur dieses entfernen
        if user in self.active_slots:
            if task is not None and task in self.active_slots[user]:
                self.active_slots[user].remove(task)
            else:
                # Falls kein Task übergeben, entferne das älteste
                if self.active_slots[user]:
                    self.active_slots[user].pop(0)
            # Clean up wenn keine Tasks mehr für den User
            if not self.active_slots[user]:
                del self.active_slots[user]
        # Nächsten aus der Queue holen, falls vorhanden und möglich
        # Wir iterieren über die Queue und nehmen den ersten, der reinpasst
        promoted = None
        for _ in range(self.queue.qsize()):
            queued_user, queued_task = self.queue.get()
            if self.has_free_slot(queued_user):
                self.active_slots[queued_user].append(queued_task)
                self.logger.debug(f"adding {queued_user} to active slots from queue")
                promoted = (queued_user, queued_task)
                break
            else:
                # Passt immer noch nicht, wieder hinten anstellen
                self.queue.put((queued_user, queued_task))
        return promoted if promoted else (None, None)

    def get_queue_position(self, user):
        lst = list(self.queue.queue)
        pos = [i for i, (u, _) in enumerate(lst) if u == user]
        return pos[0] + 1 if pos else None

    def get_active_users(self):
        return list(self.active_slots.keys())

    def get_active_slots_for_user(self, user):
        return list(self.active_slots[user])

    def get_queue_list(self):
        return [u for u, _ in list(self.queue.queue)]

class FishSlotManager_:

    def __init__(self, max_slots=MAX_SLOTS):
        self.max_slots = max_slots
        self.active_slots = {}  # user -> FishTask
        self.queue = Queue()

        self.logger = logging.getLogger("fish-slot-manager")
        self.logger = log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)   
                
        self.logger.debug("hello from FishSlotManager")
    def has_free_slot(self):
        self.logger.debug(f"active_slots <-> max_slots: {len(self.active_slots)} <-> {self.max_slots}")
        return len(self.active_slots) < self.max_slots

    def add_task(self, user, task):
        #self.logger.debug(f"{user} starting {task}")
        self.logger.debug(f"has_free_slot(): {self.has_free_slot()}")
        if self.has_free_slot():
            self.logger.debug(f"added fish task for {user} [ACTIVE_SLOT]")
            self.active_slots[user] = task
            return True
        else:
            self.logger.debug(f"added {user} to queue")
            self.queue.put((user, task))
            return False

    def finish_task(self, user):
        if user in self.active_slots:
            del self.active_slots[user]
        # Nächsten aus der Queue holen, falls vorhanden
        if not self.queue.empty():
            
            next_user, next_task = self.queue.get()
            self.active_slots[next_user] = next_task
            self.logger.debug(f"adding {next_user} to active slots")
            return next_user, next_task
        return None, None

    def get_queue_position(self, user):
        # Queue ist FIFO, daher Position durch Durchzählen bestimmen
        lst = list(self.queue.queue)
        for idx, (u, _) in enumerate(lst):
            if u == user:
                return idx + 1
        return None

    def get_active_users(self):
        return list(self.active_slots.keys())

    def get_queue_list(self):
        return [u for u, _ in list(self.queue.queue)]


class FishPopulation:

    #FISHIS = ["🐟", "🐠", "🐡", "🍥", "🦞", "🦐"]
    FISHIS = ["<><", "><°>", ">3)°>", "<°(--<", ">-->>^>", "><((((º>", ">--((((‘>", "<º)))}-=><"]
    #ZONKS = ["⚓", "🚲", "🥠", "🧦", "✂"]
    ZONKS = ["nada niente", "nix", "nuescht", "nichts", "a 🥠","gar nix", "ueberhaupt nix", "a 🥠", "nada","⚓", "jeeebaiiiteeed","nothing", "fish poop", "empty hands", "nix", "nothing", "blub",  "🚲", "a 🥠", "🧦", "✂", "goar nix"]
    #ZONKS = ["a 🥠","a 🥠"]
    def __init__(self, max_fish=69, max_weight=1337, min_weight=23):
        self.max_fish = max_fish
        self.max_weight = max_weight 
        self.min_weight = min_weight
        #self.population = self.create_population_with_weights(max_fish, self.min_weight, self.max_weight)
        #self.population = self.weight_mix(self.min_weight, self.max_weight, self.max_fish)
        self.population = self.distributed_random_weights(self.min_weight, self.max_weight, self.max_fish)
        random.shuffle(self.population)
        self.sorted_population = sorted(set(self.population))

    def distributed_random_weightsix(self, min_weight: int, max_weight: int, n_slots: int) -> list:
        percentages = [0.40, 0.30, 0.15, 0.10, 0.05]
        slot_counts = [int(n_slots * p) for p in percentages]
        slot_counts[2] += n_slots - sum(slot_counts)
        span = max_weight - min_weight + 1

        borders = [min_weight]
        for p in percentages[:-1]:
            borders.append(borders[-1] + int(span * p))
        borders[-1] = min(borders[-1], max_weight)
        borders.append(max_weight + 1)

        weights = []
        for i, count in enumerate(slot_counts):
            start = borders[i]
            end = borders[i+1] - 1
            if end < start:
                available = [start]
            else:
                available = list(range(start, end + 1))
            if count > len(available):
                weights += random.choices(available, k=count)
            else:
                weights += random.sample(available, k=count)
            print(sorted(set(weights)))

            print(len(weights))
        weights = sorted(set(weights))
        weights[0] = min_weight
        weights[-1] = max_weight

        random.shuffle(weights)
        return weights

    def distributed_random_weights(self, min_weight: int, max_weight: int, n_slots: int) -> list:
        percentages = [0.50, 0.30, 0.10, 0.05, 0.05]
        slot_counts = [int(n_slots * p) for p in percentages]
        slot_counts[2] += n_slots - sum(slot_counts)

        borders = []
        for i in range(6):
            border = min_weight + math.floor((max_weight - min_weight) * (i * 0.2))
            if border > max_weight:
                border = max_weight
            borders.append(border)
        borders[-1] = max_weight + 1  # exklusive Endgrenze

        weights = []
        weights = [69, min_weight, max_weight, 42, 1001]

        remaining_slots = n_slots - len(weights)
        """
        for i, count in enumerate(slot_counts):
            print(f"{n_slots} weightslen: {len(weights)}")
            if remaining_slots >= 0:
                start = borders[i]
                end = borders[i+1] - 1
                if end < start:
                    available = [start]
                else:
                    available = list(range(start, end + 1))
                if count > len(available):
                    weights += random.choices(available, k=count)
                    remaining_slots -= 1
                else:
                    weights += random.sample(available, k=count)
                    remaining_slots -= 1
                print(sorted(set(weights)))
        """
        for i, count in enumerate(slot_counts):
            if remaining_slots <= 0:
                break
            start = borders[i]
            end = borders[i+1] - 1
            available = list(range(start, end+1)) if end >= start else [start]

            k = min(count, remaining_slots)  # nicht überfüllen
            if k > len(available):
                weights += random.choices(available, k=k)
            else:
                weights += random.sample(available, k=k)
            remaining_slots = n_slots - len(weights)

        print(len(weights))
        print(weights)
        print("------")

        random.shuffle(weights)
        return weights

    def weight_mix(self, minweight: int, maxweight: int, nslots: int) -> list:

        if nslots < 2:
            raise ValueError("nslots must be greater 1")
        if maxweight <= minweight:
            raise ValueError("maxweight > minweight!")

        step = (maxweight - minweight) / (nslots)
        weights = [round(minweight + i * step) for i in range (nslots)]
        weights = sorted(set(weights))
        
        while len(weights) < nslots:
            for w in range(minweight, maxweight + 1):
                if w not in weights:
                    weights.append(w)
                    if len(weights) == nslots:
                        break
        
        weights[0] = minweight
        weights[-1] = maxweight
        print(f"fishies: {weights}")
        return weights


    def create_population_with_weights(self, max_fish, min_weight=200, max_weight=1337):
        possible_weights = list(range(min_weight, max_weight + 1))
        if max_fish > len(possible_weights):
            raise ValueError("max_fish is greater than the number of unique weights possible in the range.")
    
        population = [max_weight]
        possible_weights.remove(max_weight)
        remaining_weights = random.sample(possible_weights, max_fish - 1)
        population.extend(remaining_weights)
        random.shuffle(population)
        return population


    def get_fishi_for_weight(self, weight):
        """
        Returns the FISHI symbol for a specific weight based on its ordering in the population.
        - FISHIS[0] is for the smallest weight.
        - FISHIS[-1] is for the largest weight (max_weight).
        - The rest are distributed evenly among intermediate weights.
        """
        sorted_weights = self.sorted_population
        n = len(sorted_weights)
        fishis_count = len(self.FISHIS)
        print(f"fishis_count: {fishis_count}")
        if n < fishis_count:
            
            raise ValueError("Population must be at least as large as FISHIS list.")

        # Find index of the weight in the sorted population
        idx = sorted_weights.index(weight)

        if idx == 0:
            return self.FISHIS[0]
        elif idx == n - 1:
            return self.FISHIS[-1]
        else:
            # Distribute remaining fishis over intermediate weights
            # Map idx 1...(n-2) to FISHIS[1]...(FISHIS[-2])
            step = (n - 2) / (fishis_count - 2)
            fishi_idx = 1 + int((idx - 1) / step)
            # Clamp index to allowed range
            fishi_idx = min(fishi_idx, fishis_count - 2)
            return self.FISHIS[fishi_idx]

    def catch_fish(self):
        if not self.population:
            return -1, "nothing. there are no fishis left !fish fishigone"
        gramm = self.population.pop()
        if random.choice([True, False]):

            return gramm, self.get_fishi_for_weight(gramm)
        else:
            self.population.insert(0, gramm)
            return -1, random.choice(self.ZONKS)
        
    def fish_left(self):
        return len(self.population)

    def reset(self):
        self.population = list(range(1, self.max_fish+1))
        random.shuffle(self.population)


class FishHighscore:

    def __init__(self):
        self.top_score = (None, 0)
        self.low_score = (None, float('inf'))
        self.first_catch = None

    def update(self, user, gramm):
        is_top = False
        is_low = False
        is_first = False
        if gramm > 0:
            if gramm > self.top_score[1]:
                self.top_score = (user, gramm)
                is_top = True
            if gramm < self.low_score[1]:
                self.low_score = (user, gramm)
                is_low = True
            if not self.first_catch:
                self.first_catch = (user, gramm)
                is_first = True
        return is_top, is_low, is_first

    def get_highscore(self):
        return self.top_score

    def get_lowscore(self):
        return self.low_score

    def get_firstcatch(self):
        return self.first_catch

    def reset(self):
        self.top_score = (None, 0)
        self.low_score = (None, float('inf'))
        self.first_catch = None

class FishHighscore:

    def __init__(self):
        self.top_score = (None, 0)
        self.low_score = (None, float('inf'))
        self.first_catch = None

    def update(self, user, gramm):
        is_top = False
        is_low = False
        is_first = False
        if gramm > 0:
            if gramm > self.top_score[1]:
                self.top_score = (user, gramm)
                is_top = True
            if gramm < self.low_score[1]:
                self.low_score = (user, gramm)
                is_low = True
            if not self.first_catch:
                self.first_catch = (user, gramm)
                is_first = True
        return is_top, is_low, is_first

    def get_highscore(self):
        return self.top_score

    def get_lowscore(self):
        return self.low_score

    def get_firstcatch(self):
        return self.first_catch

    def reset(self):
        self.top_score = (None, 0)
        self.low_score = (None, float('inf'))
        self.first_catch = None

class FishGame:
    # TODO init from bait-hist
    def __init__(self, logger=None):
        self.slots = FishSlotManager()
        self.population = FishPopulation()
        self.bait_slot_manager = RandomBaitSlotManager()
        self.highscore = FishHighscore()
        self.fishstats = FishStats()
        self.logger = logging.getLogger(__name__)
        self.logger = log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)   

        self.stream_online = False
        
        # Registriere Event-Handler
        subscribe_event("fish_bait", self.on_bait)
        subscribe_event("fish_dynamite", self.on_dynamite)
        #subscribe_event("mytopbait_event", None)
        #subscribe_event("topbait_event", None)
        subscribe_event("topbait_command", self.on_topbait)
        subscribe_event("total_bait", self.on_topbait)
        subscribe_event("mytopbait_command", self.on_mytopbait)
        subscribe_event("set_stream_online", self.set_stream_online)
        subscribe_event("mytopbait_command_maxgramm", self.on_mytopbait_maxgramm)
        subscribe_event("mytopbait_command_personal", self.mytopbait_command_personal)
        subscribe_event("mybaitstats_command", self.mybaitstats_command)
        subscribe_event("obs_hangry_cat", self.on_obs_hangry_cat)
        subscribe_event("fishis_left", self.on_fishis_left)

        self.logger.debug("---------------------->init success")
        self.init_bait_quotes()
        self.logger.debug(f"---------------------->init success {type(self.bait_quotes)}")

    def end_bait(self):
        # -> stats in DB schreiben
        # beenden
        db_handler.insert_bait_stats(self.fishstats.get_all_user_bait_stats())

    def init_bait_quotes(self):
        self.logger.debug("blub blub blub")
        self.bait_quotes = bait_quotes_array()
    def set_stream_online(self, event_data):
        value = event_data.get("event_data")
        self.stream_online = value
        self.logger.debug(f"set_strea_online: event_data:{event_data}")
        self.logger.debug(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaa set_stream_online: {self.stream_online}")

    def on_bait(self, user):
        self.logger.debug(f"######################################################type(user){type(user)} ; {user}")
        task = FishTask(user)
        got_slot = self.slots.add_task(user, task)
        if got_slot:
            self.logger.info(f"{user} got active fishing slot")
            slot_text = self.bait_slot_manager.assign_slot()
            if not slot_text:
                self.logger.error("No free bait slots available!")
                
                return
            task.slot_text = slot_text
            delay = random.uniform(10,66)
            self.logger.info(f"{user} wait {delay:.1f}")
            timer = threading.Timer(delay, self.process_task, args=(user, task))
            timer.start()
            # TODO OBS EVENT_BASED...... refactor in refactor
            #set_source_visibility_wrapper("fishers", slot_text, True)
            post_event("obs_set_source_visibility", {"event_type": "obs_set_source_visibility", "event_data":{"scene_name": "fishers", "source_name": slot_text, "visible": True}})
            filename = f"/home/sna/src/twitch-irc/obs_websocket/fishers/{slot_text}.txt"
            file_io.write_file(filename, "w", user)
        else:
            pos = self.slots.get_queue_position(user)
            self.logger.critical(f"{user} enqueue (pos {self.slots.queue.qsize()}).")
            msg = f"queued {user} pos: {self.slots.queue.qsize()}"
            post_event("fish_queued", {"user": user, "position": pos})
            #post_event("irc_send_message", msg)

    def get_queue_positions(self, user):
        lst = list(self.queue.queue)
        return [i + 1 for i, (u, _) in enumerate(lst) if u == user]

    def get_max_baits(self, event_data):
        msg = f"{ self.fishstats.total_catches()} bait's wurden bisher geworfen"
        post_event("irc_send_message",msg)

    def on_topbait(self, event_data):
        msg =self.fishstats.top_bait()
        post_event("irc_send_message", msg)

    def on_mytopbait(self,event_data):
        self.logger.debug(f"event_data: {event_data}")
        
        user = event_data.get("event_data")
        match self.fishstats.personal_top_bait(user):
            case (gramm, fisch):
                msg = (f"{user} 's topbait: {gramm}g {fisch}")
            case None:
                msg = (f"{user} FishingeDespair try !bait first")
        #msg = user+" 's topbait: "+ str(msg) + "g"
        post_event("irc_send_message", msg)
    def on_mytopbait_maxgramm(self, event_data):
        msg = event_data.get('event_data') +" "
        msg += self.fishstats.personal_catch_gramm_string(event_data.get("event_data"))
        post_event("irc_send_message", msg)
    def mytopbait_command_personal(self, event_data):
        user = event_data.get("event_data")
        msg = user+" "
        msg += self.fishstats.personal_catches_string(user)
        post_event("irc_send_message", msg)

    def mybaitstats_command(self, event_data):
        user = event_data.get("event_data")
        msg = self.fishstats.generate_mybaitstats_string(user) 
        self.logger.debug(f"msg {msg}")
        post_event("irc_send_message", msg)

    def on_fishis_left(self, event_data):
        fishies_left = len(self.population.population)
        fishies_total = len (self.population.sorted_population)
        msg = f"there are {fishies_left} fishis left from a total of {fishies_total} fishis!"
        post_event("irc_send_message", msg)

    def process_task(self, user, task):
        gramm, fish = self.population.catch_fish()
        task.result = (gramm, fish)
        is_top, is_low, is_first = self.highscore.update(user, gramm)
        msg_irc, msg_obs = self.make_result_message(user, gramm, fish, is_top, is_low, is_first)
        #post_event("fish_result", {"user": user, "message_irc": msg_irc, "message_obs": msg_obs})
        self.logger.debug(f"{hasattr(task, "slot_text")} hasatrr? {task.slot_text}")
        if hasattr(task, "slot_text"):

            #set_source_visibility_wrapper("fishers", task.slot_text, False)
            post_event("obs_set_source_visibility", {"event_type": "obs_set_source_visibility", "event_data":{"scene_name": "fishers", "source_name": task.slot_text, "visible": False}})
            f = f"/home/sna/src/twitch-irc/obs_websocket/fishers/{task.slot_text}.txt"
            self.bait_slot_manager.release_slot(task.slot_text)
            file_io.write_file(f, "w", "")
            file_io.write_file("/home/sna/5n4fu_stream/obs_files/fishis/bait_history.txt", "a", msg_obs)
        self.logger.debug(f"before send msg: stream_online: {self.stream_online}")
        self.logger.debug(f"fishi: {fish}")
        if not self.stream_online:
            if fish == "a 🥠":
                self.logger.debug(f"cookie gotten from if fish")
            else:
                post_event("irc_send_message", msg_irc)
        
        self.fishstats.record_catch(user, gramm, fish)
        post_event("create_vip_points_chart", "")
        if is_top and not gramm == -1:

            file_io.write_top_baiter(user)
        
        if fish == "a 🥠":
            self.logger.debug(f"{len(self.bait_quotes)} {type(self.bait_quotes)}")
            x = random.randint(0, len(self.bait_quotes)-1)
            s =  f"{user} got a fortune🥠{self.bait_quotes[x]}"
            post_event("irc_send_message",s)
        if gramm==69:
            post_event("trigger_event_board", "sexy_fish.webm")
        if gramm in [23,42,66,96,1337,1001]:
            flashvids = ["flashfish.webm","falshfish_2.webm","dori_light.webm"]
            rnd = random.choice(flashvids)
            self.logger.debug(f"random flash-video: {rnd}")
            post_event("trigger_event_board", rnd)
            post_event("irc_send_message", f"{user} u lucky bastard: fishcc ChillGirl lanternfish1 , +1 event point")
            
            post_event("snafu_flash_event", {"sna"})
        next_user, next_task = self.slots.finish_task(user)
        
        if next_user and next_task:
            delay = random.uniform(10,66)
            self.logger.info(f"starting queued-bait {next_user} | queue-size: {self.slots.queue.qsize()}")
            msg=f"next from queue: {next_user},  {delay:.1f} "
            self.logger.info(f"{user} got active fishing slot")
            slot_text = self.bait_slot_manager.assign_slot()
            if not slot_text:
                self.logger.error("No free bait slots available!")
                
                return
            next_task.slot_text = slot_text
            delay = random.uniform(10,66)
            self.logger.info(f"{user} wait {delay:.1f}")

            # TODO OBS EVENT_BASED...... refactor in refactor
            set_source_visibility_wrapper("fishers", slot_text, True)
            f = f"/home/sna/src/twitch-irc/obs_websocket/fishers/{next_task.slot_text}.txt"
            file_io.write_file(f, "w", next_user)
            #post_event("irc_send_message", msg)
            timer = threading.Timer(delay, self.process_task, args=(next_user, next_task))
            timer.start()
        post_event("get_score_chart_values", None)

    def on_obs_hangry_cat(self,event_data):
        event_data = event.get("event_data")
        weighted_user = event_data.get("user")
        # TODO choose fish/player who looses a fish
        raise NotImplementedError

    def on_dynamite(self, user):
        #fishresult {'user': 'roll0r', 'message': 'roll0r jeBaited u got 🧦.'}
        results = []
        for _ in range(3):
            gramm, fish = self.population.catch_fish()
            is_top, is_low, is_first = self.highscore.update(user, gramm)
            results.append({"gramm": gramm, "fish": fish, "top": is_top, "low": is_low, "first": is_first})
        post_event("fish_dynamite_result", {"user": user, "results": results})

    def make_result_message(self, user, gramm, fish, is_top, is_low, is_first):
        if gramm > 0:
            x = f"{user} caught {fish} {gramm}g!"
            msg_irc=""
            msg_obs=""
            if is_first:
                msg_irc += "First catch of the day! "
            elif is_top:
                msg_irc += "!highscore "
            elif is_low:
                msg_irc += "!bonk "
            msg_irc += x
            msg_obs = f"{user}: {gramm}g {fish}\n"

        else:
            msg_irc = f"jeBaited {user} you've got {fish}"
            msg_obs = f"{user}: jeBaited \n"
        return msg_irc, msg_obs

class FishTask:

    def __init__(self, user):
        self.user = user
        self.result = None
        self.slot_text = ""

class FishStats:
    def __init__(self):
        self.lock = threading.Lock()
        self.catches = []  # List of dicts: {"user": str, "gramm": int, "fish": str, "timestamp": float}
        self.user_catch_count = defaultdict(int)
        self.user_total_baits = defaultdict(int)
        self.user_total_gramm = defaultdict(int)
        self.user_jebaited = defaultdict(int)
        self.user_event_bait = defaultdict(int)
        self.user_cookie_bait = defaultdict(int)
        self.user_top_bait = dict()  # user -> (gramm, fish)
        self.total_baits= 0
        self.chart_data = []
        self.chart_participants = defaultdict(str)
        subscribe_event("get_score_chart_values", self.get_score_chart_values)
        subscribe_event("create_vip_points_chart", self.create_vip_points_chart)
        subscribe_event("finish_vip_chart_with_profile_pics", self.create_vip_points_chart_part2)
        self.logger = logging.getLogger("FISHI STATS -->")
        self.logger = log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)   
 
    def record_catch(self, user, gramm, fish):
        with self.lock:
            entry = {
                "user": user,
                "gramm": gramm,
                "fish": fish,
                "timestamp": time.time(),
            }
            self.register_first_baiters(user)

            self.total_baits +=1 

            x = f"{self.total_baits}"
            write_bait_counter(x)
            # TODO write bait counter??... check.

            self.user_total_baits[user]+=1
            if gramm > 0:
                self.user_catch_count[user] += 1
                self.catches.append(entry) # without -1
                self.user_total_gramm[user] += gramm
                if (user not in self.user_top_bait) or (gramm > self.user_top_bait[user][0]):
                    self.user_top_bait[user] = (gramm, fish)
            else:
                if fish == "a 🥠":
                    self.user_cookie_bait[user] += 1
                    self.logger.debug(self.user_cookie_bait)
                self.user_jebaited[user] += 1

            if gramm in [42,23,66, 69, 96,420,1001,1337]:
                # TODO make it visible in obs / chat.
                self.user_event_bait[user]+=1
                msg = f"{user}, u caught an eventfish with {gramm} gramm! +1 event point!"
                post_event("trigger_send_message", msg)

    def register_first_baiters(self, user):
        self.logger.debug(f"in register_first_baters, {user}, len(self.user_event_bait: {len(self.user_event_bait)}")
        if len(self.user_event_bait) < 3:
            self.logger.debug(f"{user} is ... {user not in self.user_event_bait} in user_event_bait")
            if len(self.user_event_bait) == 0:
                self.user_event_bait[user] += 3
                self.logger.debug(f"{self.user_event_bait}")
                msg = f"{user} you are the first baiter! +3 event points"
                post_event("trigger_send_message", msg)
            elif len(self.user_event_bait) == 1 and user not in self.user_event_bait:
                self.user_event_bait[user] += 2
                self.logger.debug(f"{self.user_event_bait}")
                msg = f"{user} you are the second baiter! +2 event points"
                post_event("trigger_send_message", msg)
            elif len(self.user_event_bait) == 2 and user not in self.user_event_bait:
                self.user_event_bait[user] += 1
                self.logger.debug(f"{self.user_event_bait}")
                msg = f"{user} you are the third baiter! + 1 event points "
                post_event("trigger_send_message", msg)

    def top_bait(self):
        if not self.catches:
            return "no catches"
        top_catch = max(self.catches, key=lambda x: x["gramm"])
        return f"current biggest catch: {top_catch["user"]} with {top_catch["gramm"]}g {top_catch["fish"]}"
        
    def total_catches(self):
        with self.lock:
            return len(self.catches)

    def catches_per_user(self, user):
        with self.lock:
            return self.user_catch_count[user]

    def total_gramm_per_user(self, user):
        with self.lock:
            return self.user_total_gramm[user]

    def all_catches(self):
        with self.lock:
            return list(self.catches)

    def all_users(self):
        with self.lock:
            return list(self.user_catch_count.keys()) + list(self.user_jebaited.keys())

    def personal_top_bait(self, user):
        with self.lock:
            return self.user_top_bait.get(user)

    def personal_catches(self, user):
        with self.lock:
            print (f" {type(self.user_catch_count)}")

#            return self.user_catch_count[user]

    def personal_jebaited(self, user):
        with self.lock:
            return self.user_jebaited[user]

    def personal_catches_sorted(self, user):
        with self.lock:
            user_catches = [c for c in self.catches if c["user"] == user]
            return sorted(user_catches, key=lambda c: c["gramm"], reverse=True)

    def personal_catches_string(self, user):
        with self.lock:
            user_catches = [c for c in self.catches if c["user"] == user]
            sorted_catches = sorted(user_catches, key=lambda c: c["gramm"], reverse=True)
            return ", ".join(f'{c["gramm"]}g {c["fish"]}' for c in sorted_catches)

    def personal_catch_gramm_string(self, user):

        with self.lock:
            user_catches = [c["gramm"] for c in self.catches if c["user"] == user]
            sorted_gramms = sorted(user_catches, reverse=True)
            total = sum(sorted_gramms)
            return ", ".join(f"{g}g" for g in sorted_gramms) + f" (total: {total}g)"

    def top_catches_sorted_by_gramm(self, count, top=True):
        """if not TOP than reverse min->max"""
        sorted_per_user = {}
        for c in self.catches:
            user = c["user"]
            if top:
                if user not in sorted_per_user or c["gramm"] > sorted_per_user[user]:
                    sorted_per_user[user] = c["gramm"]
            else:
                if user not in sorted_per_user or c["gramm"] < sorted_per_user[user]:
                    sorted_per_user[user] = c["gramm"]
        sorted_best = sorted(sorted_per_user.items(), key=lambda x: x[1], reverse=True)
        return sorted_best[:count]

    def total_gramm_per_user_sorted(self, count):
        user_total = {}
        for catch in self.catches:
            user_total[catch["user"]] = user_total.get(catch["user"], 0) + catch["gramm"]
        return {user: total for user, total in sorted(user_total.items(), key=lambda x: x[1], reverse=True)[:count]}

    def total_jebaited_per_user(self, count):
        sorted_jebaited = sorted(self.user_jebaited.items(), key=lambda x: x[1], reverse=True)
        return sorted_jebaited[:count]

    def get_total_baits(self, top=3):
        sorted_total_baits = sorted(self.user_total_baits.items(), key=lambda x: x[1], reverse=True)
        return sorted_total_baits[:top]

    def top_total_baits(self, count=3):
        user_counts = {}
        for catch in self.catches:
            user = catch["user"]
            user_counts[user] = user_counts.get(user, 0) + 1
        return {user: count for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:count]}

    def get_top_cookie_baits(self, top=3):
        # user cookie bait
        sorted_cookies =sorted(self.user_cookie_bait.items(), key=lambda x: x[1], reverse=True)
        self.logger.debug(f"sorted cookies: {sorted_cookies}")
        return sorted_cookies[:top]

    def get_top_event_fishis(self, top=3):
        sorted_event_points = sorted(self.user_event_bait.items(), key=lambda x: x[1], reverse=True)
        return sorted_event_points[:top]
    # fishis_left == 0 -> trigger
    # short audio alert 
    # only ending? 
    # TODO event fish -> last fish + first fish. 
    def create_vip_points_chart(self, event_data):
        self.chart_participants = None
        self.participants = None
        top3 = self.top_catches_sorted_by_gramm(3)
        bottom3 = self.top_catches_sorted_by_gramm(3, False)# REVERSE POINTS!!!
        top3_jebaited = self.total_jebaited_per_user(3)
        top_cnt_baits = self.top_total_baits(3)
        top_total_weight = self.total_gramm_per_user_sorted(3)
        top_total_baits = self.get_total_baits(3)
        top_cookie_baits = self.get_top_cookie_baits(3)
        top_event_points = self.get_top_event_fishis(3)
        self.logger.debug(f"top3: {type(top3)} , {top3}")
        self.logger.debug(f"bottom3: {type(bottom3)} , {bottom3}")
        self.logger.debug(f"top3_jebaited: {type(top3_jebaited)} , {top3_jebaited}")
        self.logger.debug(f"top_cnt_baits: {type(top_cnt_baits)} , {top_cnt_baits}")
        self.logger.debug(f"top_total_weight: {type(top_total_weight)} , {top_total_weight}")
        self.logger.debug(f"top_total_baits: {type(top_total_baits)} , {top_total_baits}")
        self.logger.debug(f"top_cookie_baits: {type(top_cookie_baits)} , {top_cookie_baits}")
        self.logger.debug(f"top_event_points: {type(top_event_points)} , {top_event_points}")
        participants = defaultdict(int)
        self.logger.debug(f"participants before anything: {participants}") 
        for x, (user,xy) in enumerate(top3):
            participants[user] = 0
        for x,(user,xy) in enumerate(bottom3):
            participants[user] = 0
        for x,(user,xy) in enumerate(top3_jebaited):
            participants[user] = 0
        for (val,user) in enumerate(top_cnt_baits.keys()):
            participants[user] = 0
        for (val,user) in enumerate(top_total_weight.keys()):
            participants[user] = 0
        for x, (user,xy) in enumerate(top_total_baits):
            participants[user] = 0
        for x, (user, xy) in enumerate(top_cookie_baits):
            participants[user] = 0
        for x, (user,xy) in enumerate(top_event_points):
            participants[user] = 0
        self.logger.debug(f"participants: {participants}")
        self.chart_participants = participants
        # ------- hier split into 2 functions. da. die get_user_images dann denrest aufruft. und wir vorher die participants an getUsers schicken
        self.chart_data = [top3, 
                          bottom3, 
                          top3_jebaited, 
                          top_cnt_baits, 
                          top_total_weight, 
                          top_total_baits, 
                          top_cookie_baits, 
                          top_event_points ]
        if len(participants)>1:
            post_event("trigger_get_user_profile_imgs",list( participants.keys()) )

    def create_vip_points_chart_part2(self, event_data):
        self.logger.debug(f"............................ {event_data}")
        participants =self.chart_participants
        self.logger.debug(f"event_data: {event_data}, participants: {participants}")
        for x,(user,xy) in enumerate(reversed(self.chart_data[0])):
            participants[user] += ((x+1)*2)
            self.logger.debug(f"top3: user: {user} with {xy} counter:{x} added {(x+1)*2}")

        for x,(user,xy) in enumerate(reversed(self.chart_data[1])):
            participants[user] += len(self.chart_data[1])-x
            self.logger.debug(f"bottom3: user: {user} with {xy} counter: {x} added {len(self.chart_data[1])-x}")

        for x,(user,xy) in enumerate(self.chart_data[2]):
            participants[user] += (x+1)
            self.logger.debug(f"top3_jebaited: user: {user} with {xy} counter:{x} added {x+1}")
        
        self.logger.debug(f"self.chart_data[3] {type(self.chart_data[3])} , {self.chart_data[3]} , len: {len(self.chart_data[3])}") 
        for x, (user, xy) in enumerate(sorted(self.chart_data[3].items(), key=lambda kv: kv[1], reverse=True)):
        #for x,(user,xy) in enumerate(reversed(self.chart_data[3])):
           participants[user] += ((x+1)*2)
           self.logger.debug(f"top3_total_baits: user: {user} with {xy} counter:{x} added {(x+1)*1}")
        
        self.logger.debug(f"self.chart_data[4] {type(self.chart_data[4])} , {self.chart_data[4]} , len: {len(self.chart_data[4])}") 
        n = len(self.chart_data[4])
        for x, user in enumerate(self.chart_data[4].keys()):
            pts = (n-x)*3
            #participants[user] += ((x+1)*3)
            participants[user] += pts
            #self.logger.debug(f"top_cnt_baits: user: {user} with {top_cnt_baits.get(user)} counter:{x} added {pts}")
       
        self.logger.debug(f"self.chart_data[5] {type(self.chart_data[5])} , {self.chart_data[5]} , len: {len(self.chart_data[5])}") 
        n = len(self.chart_data[5])
        for x, (user, value) in enumerate(self.chart_data[5]):
            #for x, user in enumerate(self.chart_data[5].keys()):
            pts = n -x
            participants[user] += pts
            #self.logger.debug(f"top_total_weight: user: {user} with {top_total_weight.get(user)} counter:{x} added {pts}")

        self.logger.debug(f"self.chart_data[6] {type(self.chart_data[6])} , {self.chart_data[6]} , len: {len(self.chart_data[6])}") 
        for x,(user,xy) in enumerate(reversed(self.chart_data[6])):
            self.logger.debug(f"top_cookie_baits -> user {user} , xy {xy} , x {x}")
            participants[user] += ((x+1)*2)
            self.logger.debug(f"top_cookie_bait: user: {user} with {xy} counter:{x} added {(x+1)*2}")
        
        self.logger.debug(f"self.chart_data[7] {type(self.chart_data[7])} , {self.chart_data[7]} , len: {len(self.chart_data[7])}") 
        for x,(user,xy) in enumerate(reversed(self.chart_data[7])):
            self.logger.debug(f"top_event_points -> user {user} , xy {xy} , x {x}")
            participants[user] += ((x+1)*3)
            self.logger.debug(f"top_event_user: user: {user} with {xy} counter:{x} added {(x+1)*3}")
        
        self.logger.debug(".................................................................................")
        self.logger.debug(participants)
        post_event("update_vip_fishing_chart", [participants,event_data])
        self.logger.debug(participants)

    def get_score_chart_values(self, event_data):
        
        with self.lock:
            # top weight catches
            top3 = self.top_catches_sorted_by_gramm(3)
            top_weight_str = "{ " + ", ".join(f'"{user}": {gramm}' for user, gramm in top3) + " }"
            # TODO reverse    
            # top bottom weights
            bottom3 = self.top_catches_sorted_by_gramm(3, False)
            bottom_weight_str = "{ " + ", ".join(f'"{user}": {gramm}' for user, gramm in reversed(bottom3)) + " }"
            # top_total_weight
            top_total_weight = self.total_gramm_per_user_sorted(3)
            # top jebaited
            top3_jebaited = self.total_jebaited_per_user(3)
            top_jebaited_str = "{ " + ", ".join(f'"{user}": {count}' for user, count in reversed(top3_jebaited)) + " }"
            # only positive counts where actually fish..
            top_cnt_baits = self.top_total_baits(3)
            # total baits thrown
            total_baits = self.get_total_baits(3)
            top_total_baits_str = "{ " + ", ".join(f'"{user}": {count}' for user, count in total_baits) + " }" 
            # top cookie baits
            top_cookies = self.get_top_cookie_baits(3)
            top_cookies_str = "{ " + ", ".join(f'"{user}": {count}' for user, count in top_cookies) + " }"
            # event-fishi-points
            top_event_fishis = self.get_top_event_fishis(3)  
            top_event_fishis_str = "{ " + ", ".join(f'"{user}": {count}' for user, count in top_event_fishis) + " }"
            chart_values = [top_weight_str, 
                            top_total_weight, 
                            top_cnt_baits, 
                            bottom_weight_str,
                            top_jebaited_str, 
                            top_total_baits_str, 
                            top_cookies_str, 
                            top_event_fishis_str ]
            self.logger.debug(f"score chart values ready: {chart_values}")    
            post_event("write_score_chart_values", chart_values) 

    def get_all_user_bait_stats(self):
        with self.lock:
            all_users = set(list(self.user_catch_count.keys()) + list(self.user_jebaited.keys()))
            result = []
            for user in all_users:
                stats = [
                     user,
                     self.user_catch_count.get(user, 0),
                     self.user_jebaited.get(user, 0),
                     self.user_total_gramm.get(user, 0)
                     ]
                print(f"{stats}")
                result.append(stats)
            return result

    def generate_mybaitstats_string(self, user):
        with self.lock:

            user_catches = [c["gramm"] for c in self.catches if c["user"] == user]
            sorted_g = sorted(user_catches)

            jebaited = (self.user_jebaited[user])
            total_catches = len(sorted_g) +jebaited 
            total_g = sum(sorted_g)
            if len(sorted_g) == 1:
                max_g = max(sorted_g)
                min_g = 0
            elif len(sorted_g) > 0:
                max_g = max(sorted_g)
                min_g = min(sorted_g)
            else:
                max_g = 0
                min_g = 0    
            
            return (f"{user} 's stats: total baits: {total_catches} | total_gramm: {total_g} | min_g: {min_g} | max_g: {max_g} | +baits: {len(sorted_g)} | jebaited: {jebaited}.")
            
    def reset(self):
        with self.lock:
            self.catches.clear()
            self.user_catch_count.clear()
            self.user_total_gramm.clear()
            self.user_jebaited.clear()
            self.user_top_bait.clear()
