from collections import deque
import asyncio

from twitchAPI.chat import ChatCommand






class AsyncFishList:

    def __init__(self):
        self._list = []
        
        self._fishing_posis = [i * 200 + 400 for i in range(10)]
        self._fishing_posis_obs = self.set_fishing_posis()
        self._fishing_slots = [None]  * 10
        self.fishing_queue  = deque()
        self._lock = asyncio.Lock()
    
        print ({str(self._fishing_posis)})
        print(f'obs-fishing-slots:  {self._fishing_posis_obs}')


    async def init(self):
        pass
        
    async def get_queue(self):
        async with self._lock:
            return list(self.fishing_queue)

    def set_fishing_posis(self):
        return ["01_bait", "02_bait", "03_bait", "04_bait", "05_bait" , "06_bait", "07_bait", "08_bait" , "09_bait" , "10_bait"]

    async def get_available_positions(self):
        async with self._lock:
            return [self._fishing_posis[i] for i, slot in enumerate(self._fishing_slots) if slot is None]

    async def get_fishing_slot(self, cmd: ChatCommand):
        """ xcowsay - position variant"""
        async with self._lock:
            try:
                free_slot = self._fishing_slots.index(None)  
           
                
                self._fishing_slots[free_slot] = {  "user": "blub",
                                                    "pos": free_slot}
                
                return self._fishing_posis[free_slot]  , free_slot
            except ValueError:
                self.fishing_queue.append(cmd)
                await cmd.reply(f"added {cmd.user.name}! queue {len(self.fishing_queue) }")
                return "queue", {len(self.fishing_queue)}  

    async def get_fishing_slot_obs(self, cmd: ChatCommand):
        async with self._lock:
            try:
                free_slot = self._fishing_slots.index(None)
                #print(f'{free_slot} + obs')
                self._fishing_slots[free_slot] = { "user": cmd.user.name,
                                                    "pos": free_slot}
                return self._fishing_posis_obs[free_slot], free_slot
            except ValueError:
                self.fishing_queue.append(cmd)
                await cmd.reply(f"added {cmd.user.name}! queue {len(self.fishing_queue) }")
                return "queue", len(self.fishing_queue)  


    async def add_catch(self, user: str, weight: float):
        
        async with self._lock:
            #fishing_slot = await self.get_fishing_slot(user)
            #if fishing_slot != None:
            #    print(f'fishing_slot: {fishing_slot}')
            self._list.append({"user": user, "weight": weight})

    async def free_fishing_slot(self,free_slot,cmd):
        async with self._lock:
            self._fishing_slots[free_slot] = None

            if self.fishing_queue:
                next_user = self.fishing_queue.popleft()
                await cmd.reply(f'{cmd.user.name} next in queue')



    async def free_fishing_slot_obs(self,free_slot,cmd):
        async with self._lock:
            self._fishing_slots[free_slot] = None

            if self.fishing_queue:
                next_user = self.fishing_queue.popleft()
                await cmd.reply(f'{cmd.user.name} next in queue')

    async def is_best_or_worst_catch(self, weight: float):
        
        async with self._lock:
            if not self._list: 
                return "first"

            weights = [entry["weight"] for entry in self._list]
            max_weight = max(weights)
            min_weight = min(weights)
            print(f'{min_weight > weight} = min_weight > weight')
            if max_weight == min_weight:
                return False
            elif  min_weight > weight:
                print (f'weight: {weight} - min_weight: {min_weight}')
                return True
            elif weight > max_weight:
                print (f'weight: {weight} - max_weight: {max_weight}')
                return False
            
            else:
                print (f'weight: {weight} - min_weight: {min_weight} max_weight: {max_weight}')
                return None
    async def is_first_catch(self, weight):
        async with self._lock:
            if not self._list:
                return True
            else:
                return False
            
    # morzis worte: TARGET <-> is_top
    # type()
    
    async def is_bait_top_or_low(self, weight: int , is_top: bool):
        async with self._lock:
            if not self._list:
                return -1
            weights = [entry["weight"] for entry in self._list]
            if is_top:
                target_weight = max(weights)
                return weight < target_weight
                
            target_weight = min(weights)
            return weight < target_weight
            

            
    async def is_top_bait(self, weight):
        
        async with self._lock:
            #print(f"before: {self._list}")
            if not self._list:
                #print("returned from self._lsit")
                return True

            weights = [entry["weight"] for entry in self._list]
            max_weight = max(weights)
            #print(f' {max_weight} < {weight} ..............................')
            if max_weight < weight:
                print("returned from max_weight < weight")
                return True
            else:
                return False

    async def is_low_bait(self, weight):
        async with self._lock:
            if not self._list:
                return True
            weights = [entry["weight"] for entry in self._list]
            min_weight = min(weights)

            if int(min_weight) > int(weight):
                return True
            return False 

    async def get_all_catches(self):
        
        async with self._lock:
            return list(self._list)
        

    async def get_catches_by_user(self, user: str):
        
        async with self._lock:
            return [entry for entry in self._list if entry["user"] == user]
    
    async def get_catches_by_user_as_string(self, user: str, as_string: bool):
        # changed! mit morzi!
        async with self._lock:
            user_catches = [entry["weight"] for entry in self._list if entry["user"] == user]
            
            if as_string:
                if not user_catches:
                    return f"{user} no catches"

                total_catches = len(user_catches)
                weights_str = "->".join(f"{w}g" for w in sorted(user_catches, reverse=True))
                
                return f"{user} {total_catches} catches (total), {weights_str}"
            
            return user_catches


    async def get_top_catch(self):
        
        async with self._lock:
            return max(self._list, key=lambda x: x["weight"], default=None)

    async def clear_list(self):
        
        async with self._lock:
            self._list.clear()

    async def get_user_with_biggest_catch(self):
        
        top_catch = await self.get_top_catch()
        return top_catch["user"] if top_catch else None

    async def get_top_catches(self, n=3):
        
        async with self._lock:
            return sorted(self._list, key=lambda x: x["weight"], reverse=True)[:n]


    async def get_top_3_as_string(self):

        top_catches = await self.get_top_catches(3)
        return ", ".join(f"{entry['user']}: {entry['weight']}g" for entry in top_catches)




