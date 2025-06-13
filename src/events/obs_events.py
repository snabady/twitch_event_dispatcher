import logging
import os
import asyncio
import json
import simpleobsws
from dotenv import load_dotenv

password = "password"
obs_url = "ws://127.0.0.1:4455"
ws = None


def setEnv():
    """
    loads the .env variables
    adjust variables in .env File 
    """
    global password, host, port,obs_url
    host       = os.getenv("OBS_WS_HOST") 
    port       = os.getenv("OBS_WS_PORT")
    password   = os.getenv("OBS_WS_PASS")

    
    obs_url = "ws://" + str(host) + ":" + str(port)
    print(obs_url)

def init_obswebsocket_ws():
    global ws
    ws  = simpleobsws.WebSocketClient(url=obs_url, password=password)
    await ws.connect()
    await ws.wait_until_identified()


def get_scene_item_id(scene_name, source_name):
    ''' it is actually the source_id...'''
    global ws
    request = simpleobsws.Request("GetSceneItemId", {
                        "sceneName": scene_name,
                        "sourceName": source_name
                    })
    response = await ws.call(request)
    if response.ok():
        return response.responseData["sceneItemId"]
    else:
        return Null

def set_source_visibility(scene_name, scene_item_id, visible=False):
    global ws
    request = simpleobsws.Request("SetSceneItemEnabled", {
                        "sceneName": scene_name, 
                        "sceneItemId": scene_item_id,
                        "sceneItemEnabled": visible
                    })
    response = await ws.call(request)
    if response.ok():
        return True
    return False 



async def on_event(eventType, eventData):
    print('New event! Type: {} | Raw Data: {}'.format(eventType, eventData)) # Print the event data. Note that `update-type` is also provided in the data

async def on_switchscenes(eventData):
    print('Scene switched to "{}".'.format(eventData['sceneName']))


async def sna():
    global password,obs_url
    load_dotenv(override=True)
    setEnv()

    print(f'hello? {obs_url}')
    #global ws
    #ws  = simpleobsws.WebSocketClient(url='ws://127.0.0.1:4455', password=password)
    
    #await ws.connect()
    #await ws.wait_until_identified()
    #logging.info('Connected and identified.')
    
    await init_obswebsocket_ws()

    req = simpleobsws.Request('GetSceneList')
    response = await ws.call(req)
    
    data = response.responseData
    scenes = data.get("scenes")
    
    raid_id = await get_scene_item_id("main","raid")
    await set_source_visibility("main",raid_id,True)
    return

    for x in scenes:
        scene = x.get("sceneName")
        uuid = x.get("sceneUuid")
        
        req = simpleobsws.Request("GetSceneItemList", {'sceneName':scene, 'sceneUuid':uuid})
        response = await ws.call(req)
        
        if response.ok():
            data = response.responseData
        
            scene_items = data.get("sceneItems")
            
            for x in scene_items:
                source_name = x["sourceName"]
                source_uuid = x["sourceUuid"]
                source_item_id = x["sceneItemId"]
                print(source_name)
                if source_name == 'cam':
                    print(f"---------------------------{source_name}")
                    print(f'{source_name} ... {source_uuid}')
                    print(source_name == 'cam')
                    print(source_name is 'cam')
                    
                    

                    #request = simpleobsws.Request("SetSceneItemEnabled", {'sceneUuid':source_uuid, 'sceneItemId':source_item_id, 'sceneItemEnabled':1})
                    #cam_input_settings_req = simpleobsws.Request("GetInputSettings")
                    #cam_input_settings = await ws.call(cam_input_settings_req)
                    #print(cam_input_settings)

                    #request = simpleobsws.Request("GetSceneItemId", {
                    #    "sceneName": "main",
                    #    "sourceName": "cam"
                    #})
                    #response = await ws.call(request)
                    #scene_item_id = response.responseData["sceneItemId"]#
                    scene_item_id = await get_scene_item_id("main", "cam")
                    print(f'scene_item_id: {scene_item_id}')

                    request = simpleobsws.Request("SetSceneItemEnabled", {
                        "sceneName": "main", 
                        "sceneItemId": scene_item_id,
                        "sceneItemEnabled": True
                    })
                    # read settings
                    request = simpleobsws.Request("GetSceneItemTransform", { 
                                                            "sceneName": "main", 
                                                            "sceneItemId": scene_item_id
                                                            })
                    response = await ws.call(request)
                    
                    print(response)
                    response = response.responseData
                    old_positionX   = response["sceneItemTransform"]["positionX"]
                    old_positionY   = response["sceneItemTransform"]["positionY"]
                    old_width       = response["sceneItemTransform"]["width"]
                    old_height      = response["sceneItemTransform"]["height"]
                    #set settings
                    new_width = old_width
                    new_height = old_height
                    new_positionX = old_positionX + (old_width - new_width)
                    new_positionY = old_positionY + (old_height - new_height)

                    sceneItemTransform = {}
                    sceneItemTransform['scaleX'] = 0.20
                    sceneItemTransform['scaleY'] = 0.20
                    request = simpleobsws.Request("SetSceneItemTransform", {
                                                            "sceneName": "main", 
                                                            "sceneItemId": scene_item_id, 
                                                            "sceneItemTransform": sceneItemTransform
                                                            })
                    response = await ws.call(request)
                    
                    print(response)
                    if response.ok():
                        "cam should be changed."
                        return


                   #request = simpleobsws.Request("SetInputSettings", {"inputUuid": source_uuid, "inputSettings": {"visible": False}, "overlay":False })
                   # response = await ws.call(request)
                   # if response.ok():
                    #    print("cam OFF")
                    #    print("---------------------------")
                    #    return
                    #else:
                    #    print(response)
                    #    print("--------------------🎏t-------")
                    #    return
            #await asyncio.sleep(10)
        else:
            
            print("MOEEEEP MOEEEEP")

    


    
    
#load_dotenv(override=True)  
#setEnv()
asyncio.run(sna())
#ws  = simpleobsws.WebSocketClient(url='ws://127.0.0.1:4455', password=password)
#loop = asyncio.get_event_loop()
#loop.run_until_complete(init())
#ws.register_event_callback(on_event) # By not specifying an event to listen to, all events are sent to this callback.
#ws.register_event_callback(on_switchscenes, 'SwitchScenes')
#loop.run_forever()
