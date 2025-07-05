import random
import logging
from utils import log
from queue import Queue
import threading
from dispatcher.event_dispatcher import post_event, subscribe_event
import time
from collections import defaultdict
from utils import file_io
from events.obsws import set_source_visibility_wrapper

MAX_SLOTS           = 10
USER_MAX_SLOTS      = 3


class RandomBaitSlotManager:
    def __init__(self, max_slots=10):
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

        self.logger = logging.getLogger(__name__)
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
    FISHIS = ["<><", "><>", ">33))°>", "<°((--<", ">->>^>", "><(((º>", "><(((‘>", "<º)))><"]
    ZONKS = ["⚓", "🚲", "🥠", "🧦", "✂"]

    def __init__(self, max_fish=5000):
        self.max_fish = max_fish
        self.population = self.create_population_with_weights(max_fish)
        random.shuffle(self.population)

    def create_population_with_weights(self, max_fish, min_weight=200, max_weight=600):
        return [random.randint(min_weight, max_weight) for _ in range(max_fish)]

    def catch_fish(self):
        if not self.population:
            return -1, random.choice(self.ZONKS)
        gramm = self.population.pop()
        if random.choice([True, False]):
            return gramm, random.choice(self.FISHIS)
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


class FishGame:

    def __init__(self, logger=None):
        self.slots = FishSlotManager()
        self.population = FishPopulation()
        self.bait_slot_manager = RandomBaitSlotManager()
        self.highscore = FishHighscore()
        self.fishstats = FishStats()
        self.logger = logger or logging.getLogger("FishGame")
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

    def set_stream_online(self, event_data):
        value = event_data.get("event_data")
        self.stream_online = value

    def on_bait(self, user):
        self.logger.debug(f"type(user){type(user)} ; {user}")
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
        post_event("irc_send_message", {"event_type": "irc_chat_command", 
                                        "event_data": msg})

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

    def process_task(self, user, task):
        gramm, fish = self.population.catch_fish()
        task.result = (gramm, fish)
        is_top, is_low, is_first = self.highscore.update(user, gramm)
        msg_irc, msg_obs = self.make_result_message(user, gramm, fish, is_top, is_low, is_first)
        #post_event("fish_result", {"user": user, "message_irc": msg_irc, "message_obs": msg_obs})
        self.logger.debug(f"{hasattr(task, "slot_text")} hasatrr? {task.slot_text}")
        if hasattr(task, "slot_text"):

            set_source_visibility_wrapper("fishers", task.slot_text, False)
            post_event("obs_set_source_visibility", {"event_type": "obs_set_source_visibility", "event_data":{"scene_name": "fishers", "source_name": task.slot_text, "visible": False}})
            f = f"/home/sna/src/twitch-irc/obs_websocket/fishers/{task.slot_text}.txt"
            self.bait_slot_manager.release_slot(task.slot_text)
            file_io.write_file(f, "w", "")
        if self.stream_online:

            self.logger.debug("stream online, no irc msg")
            file_io.write_file("/home/sna/5n4fu_stream/obs_files/fishis/bait_history.txt", "a", msg_obs)
        else:
            post_event("irc_send_message", msg_irc)
        self.fishstats.record_catch(user, gramm, fish)
        # Task beenden und nächsten aus der Queue holen
        next_user, next_task = self.slots.finish_task(user)
        if next_user and next_task:
            # --- RANDOM DELAY für Nachrücker ---
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
    """
    Speichert Statistiken zu allen Fängen und bietet persönliche Auswertungen:
    - Liste aller Fänge
    - Gesamtanzahl der Fänge
    - Anzahl der Fänge pro User
    - Gesamtgewicht pro User
    - Liste der Fänge pro User
    - Persönlicher Top-Bait
    - Persönliche Anzahl der Catches
    - Persönliche Anzahl der jeBaited (Zonks)
    Threadsafe.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.catches = []  # List of dicts: {"user": str, "gramm": int, "fish": str, "timestamp": float}
        self.user_catch_count = defaultdict(int)
        self.user_total_gramm = defaultdict(int)
        self.user_jebaited = defaultdict(int)
        self.user_top_bait = dict()  # user -> (gramm, fish)

    def record_catch(self, user, gramm, fish):
        with self.lock:
            entry = {
                "user": user,
                "gramm": gramm,
                "fish": fish,
                "timestamp": time.time(),
            }
            self.catches.append(entry)
            if gramm > 0:
                self.user_catch_count[user] += 1
                self.user_total_gramm[user] += gramm
                # update personal top bait
                if (user not in self.user_top_bait) or (gramm > self.user_top_bait[user][0]):
                    self.user_top_bait[user] = (gramm, fish)
            else:
                self.user_jebaited[user] += 1
    def top_bait(self):
        if not self.catches:
            return "no catches"
        top_catch = max(self.catches, key=lambda x: x["gramm"])
        return f" {top_catch["user"]} with {top_catch["gramm"]}g {top_catch["fish"]}"

        
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

    # Neue Funktionen für Statistiken:
    def personal_top_bait(self, user):
        
        with self.lock:
            return self.user_top_bait.get(user)

    def personal_catches(self, user):
        """Anzahl der erfolgreichen Fänge (keine Zonks) für den User."""
        with self.lock:
            return self.user_catch_count[user]

    def personal_jebaited(self, user):
        """Anzahl der jeBaited (Zonks) für den User."""
        with self.lock:
            return self.user_jebaited[user]

    def reset(self):
        with self.lock:
            self.catches.clear()
            self.user_catch_count.clear()
            self.user_total_gramm.clear()
            self.user_jebaited.clear()
            self.user_top_bait.clear()