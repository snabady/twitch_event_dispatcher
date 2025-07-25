import requests
import asyncio
import time
import logging
import threading
from utils import log 
from dispatcher.event_dispatcher import subscribe_event

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        #cls._instances[cls] = super(Singleton, cls).__call__(*args,**kwargs)
        #return cls._instances[cls]
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class WLEDController(metaclass=Singleton):
    def __init__(self, ip_address):
        
        self.base_url = f"http://{ip_address}/json/state"
        self.chatstrobo = 0
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)
        #self.strobo_thread = threading.Thread(target=self.check_strobo, daemon=True)
        #self.strobo_thread.start()
        self.logger.debug("subscribing to snafu_flash_event")
        subscribe_event("snafu_flash_event", self.add_chatstrobo)

    def set_effect(self, effect_id, color=(255, 255, 255), brightness=128, segment_id=0, on=True):
        payload = {
            "on": on,
            "bri": brightness,
            "seg": [{
                "id": segment_id,
                "fx": effect_id,
                "col": [[color[0], color[1], color[2]]]
            }]
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=2)
            response.raise_for_status()
            print(f"set effect# {effect_id}")
        except requests.RequestException as e:
            print(f"set WLED effect - somesthing went wrong  {e}")
    
    
    def add_chatstrobo(self, event):
        self.chatstrobo +=1


    async def start(self):
        asyncio.create_task(self.check_strobo())

    async def check_strobo(self):
        self.logger.debug("running checkstrobo loop")
        while True: 
            if self.chatstrobo > 0:
                print (f'chatstrobo_cnt: {self.chatstrobo}')
                self.set_preset(24)
                self.chatstrobo -=1
            await asyncio.sleep(0.5)


    def set_preset(self, preset_id):
        payload = {"ps": preset_id}

        try:
            response = requests.post(self.base_url, json=payload, timeout=2)
            response.raise_for_status()
            print(f"set preset:  {preset_id}")
        except requests.RequestException as e:
            print(f"set preset effect -something went wrong: {e}")

    def turn_off(self):
        try:
            response = requests.post(self.state_url, json={"on": False}, timeout=2)
            response.raise_for_status()
            print("WLED: good night")
        except requests.RequestException as e:
            print(f"wled goodnight went wrong {e}")



    
