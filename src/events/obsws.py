import logging
import os
import asyncio
import json
import simpleobsws
from utils import log
from dispatcher.event_dispatcher import post_event, subscribe_event
from simpleobsws import enum as enums
from handlers import obs_handler

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   
# TODO check bait, really 3 times source visibility=?
# TODO re-login
# TODO if offline.... check...!


def set_source_visibility_wrapper(scene_name, source_name, visible):
    
#    logger.debug(f'scene_name: {scene_name}\tsource_name: {source_name}\tvisible: {visible}')
    async def runner():
        obs = Obsws()
        scene_item_id = await obs.get_scene_item_id(scene_name, source_name)        
        await obs.set_source_visibility(scene_name, scene_item_id, not visible)
        await asyncio.sleep(0.1)
        await obs.set_source_visibility(scene_name, scene_item_id, visible)

    Obsws().enqueue(runner())#.put_nowait(runner())

def switch_scene_wrapper(scene_name: str):
    async def runner():
        obs = Obsws()
        await obs.switch_scene(scene_name)
    Obsws().enqueue(runner())

def trigger_hotkey_by_name_wrapper(hotkey_name: str):
    async def runner():
        obs=Obsws()
        await obs.trigger_hotkey_by_name(hotkey_name)
    Obsws().enqueue(runner())

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        #cls._instances[cls] = super(Singleton, cls).__call__(*args,**kwargs)
        #return cls._instances[cls]
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Obsws(metaclass=Singleton):

    def __init__(self):
        self.obs_task_queue = asyncio.Queue()
        self.ws = None
        self.logger = logging.getLogger("OBSWS")
        if not self.logger.hasHandlers():
            log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)
        asyncio.create_task(self.obs_task_worker())
        self.logger.debug("Hello from obsws")
        #asyncio.create_task(self.subscribe_events())
        self.stream_online = False
        subscribe_event("obs_set_source_visibility", self.obs_set_source_visibility)
        subscribe_event("obs_scene_change", self.obs_scene_change)
        subscribe_event("obs_set_input_mute", self.obs_set_input_mute)
        self.setEnv()
        self.set_event_map()
   
    async def __aenter__(self):

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.ws.disconnect()

    def setEnv(self):
        """
        loads the .env variables
        adjust variables in .env File 
        """
        self.obs_url     = os.getenv("OBSWS_URL", "nope obs-url .env")
        #self.obs_url = "ws://" + str(self.host) + ":" + str(self.port)
        #self.obs_url = "ws://127.0.0.1:4455"
        
        self.password = os.getenv("OBSWS_PASSWORD", "OBSWS_PASSWORD")

    async def obs_task_worker(self):
        while True:
            task_coro_func = await self.obs_task_queue.get()
            try:
                await task_coro_func
            except Exception as e:
                print(f"OBS_TASK_WORKER {e}")
            finally:
                self.obs_task_queue.task_done()   
            await asyncio.sleep(0.5)


    def set_event_map(self):
        self.event_map={
                "MediaInputPlaybackEnded": obs_handler.media_input_playback_ended, 
                "SceneItem":obs_handler.blub
                }


    def obs_set_source_visibility(self, event):
        event = event.get("event_data")
        if not event.get("visible"):        
            self.enqueue( self.set_source_visibility(event.get("scene_name"), event.get("source_name"), True ) )
            self.enqueue( self.set_source_visibility(event.get("scene_name"), event.get("source_name"), False ) )
        else:
            self.enqueue( self.set_source_visibility(event.get("scene_name"), event.get("source_name"), False ) )
            self.enqueue( self.set_source_visibility(event.get("scene_name"), event.get("source_name"), True ) )
        self.enqueue( self.set_source_visibility(event.get("scene_name"), event.get("source_name"), event.get("visible") ) )

    def obs_scene_change(self, event): 
        raise NotImplementedError

    def enqueue(self, coro):
        self.logger.debug(self)
        self.obs_task_queue.put_nowait(coro)
        self.logger.debug(f"OBS_QUEUE: {self.obs_task_queue.qsize()}")

    async def init_obswebsocket_ws(self):
        try:
            self.ws  = simpleobsws.WebSocketClient(self.obs_url, password=self.password)
            await self.ws.connect()
            await self.ws.wait_until_identified()
            
            #await asyncio.Future()
        except Exception as e:
            self.logger.debug(f'moep {e}')

        self.ws.register_event_callback(self.on_event)

    async def get_scene_item_id(self, scene_name, source_name):
        ''' it is actually the source_id...'''
        self.logger.debug(f"get_scene_item_id {scene_name} .. {source_name}")
        request = simpleobsws.Request("GetSceneItemId", {
                            "sceneName": scene_name,
                            "sourceName": source_name
                        })
        response = await self.ws.call(request)
        self.logger.debug(response)
        if response.ok():
            self.logger.debug(f'{scene_name}|{source_name}: got sceneItemId: {response.responseData["sceneItemId"]}')
            return response.responseData["sceneItemId"]
        else:
            self.logger.debug("response not ok, from get_scene_item_id")
            return Null

    async def set_source_visibility(self,scene_name, scene_item_id, visible=False):
        #connected = await self.ws.connect()
        #if not connected:
        #    await self.init_obswebsocket_ws()
        if isinstance(scene_item_id, str):
            scene_item_id = await self.get_scene_item_id(scene_name, scene_item_id)
        
        request = simpleobsws.Request("SetSceneItemEnabled", {
                            "sceneName": scene_name, 
                            "sceneItemId": scene_item_id,
                            "sceneItemEnabled": visible
                        })
        response = await self.ws.call(request)
        

    async def switch_scene(self, scene_name):
        request = simpleobsws.Request(
        requestType='SetCurrentProgramScene',
        requestData={'sceneName': scene_name})

        response = await self.ws.call(request)
    def obs_set_input_mute(self, event):
        event_data = event.get("event_data")
        audiosource = event_data.get("audiosource")
        muted = event_data.get("muted")

        self.enqueue( self.set_input_mute(muted, audiosource) )

    async def set_input_mute(self, muted: bool, audiosource: str):
        request = simpleobsws.Request(requestType="SetInputMute", 
                                      requestData={"inputName": audiosource,
                                                   "inputMuted": muted})
        response = await self.ws.call(request)
    

    # TODO worst things happen at sea...
    # well... this should do the handler?
    # 
    async def on_event(self, eventType, eventData):
        if eventData == None:
            self.logger.debug(f"eventType: {eventType}")
            return
        
        if eventData.get("inputName")!= "TimerText":
            self.logger.debug(eventData.get("inputName"))
        if not (eventType =="InputSettingsChanged" and eventData.get("inputName") == "TimerText"):
           self.logger.info('event_triggered Type: {} | Raw Data: {}'.format(eventType, eventData)) 
        if eventType == "MediaInputPlaybackEnded" and eventData.get("inputName") == "raid_audio":
            await self.set_input_mute(False, "desktop_audio")
            await self.set_source_visibility("ALERTS","raid_overlay", False)

    async def sna():    
        setEnv()
        self.ws = await init_obswebsocket_ws()
        await asyncio.Future()


    async def trigger_hotkey_by_name(self, hotkey_name):
        request = simpleobsws.Request("TriggerHotkeyByName", {"hotkeyName": hotkey_name})
        response = await self.ws.call(request)
        self.logger.debug(response.ok())

    async def reload_browser_source(self, browser_source_name: str):
        request = simpleobsws.Request(
            "PressInputPropertiesButton",
            {
                "inputName": browser_source_name,
                "propertyName": "refreshnocache"  
            }
        )
        response = await self.ws.call(request)
        self.logger.debug("Reload requested:", response.ok())
        await self.ws.disconnect()

    async def subscribe_events(self):
        event_subs = (
            simpleobsws.enums.EventSubscription.MediaInputs |
            simpleobsws.enums.EventSubscription.SceneItems |
            simpleobsws.enums.EventSubscription.Transitions |
            simpleobsws.enums.EventSubscription.Outputs |
            simpleobsws.enums.EventSubscription.Filters | 
            simpleobsws.enums.EventSubscription.General |
            simpleobsws.enums.EventSubscription.Config | 
            simpleobsws.enums.EventSubscription.Scenes | 
            simpleobsws.enums.EventSubscription.Inputs | 
            simpleobsws.enums.EventSubscription.Vendors | 
            simpleobsws.enums.EventSubscription.Ui 
        )
        request = simpleobsws.Request("SubscribeEvents", {
            "eventSubscriptions": event_subs
        })
        response = await self.ws.call(request)
        self.logger("Subscribed:", response.ok())
