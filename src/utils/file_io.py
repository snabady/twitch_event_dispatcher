import os
import time 
import json
from src.dispatcher.event_dispatcher import post_event
import asyncio

def write_file(filepath=str, mode= str , text= str):
    with open(filepath, mode) as f:
        f.write(text)

async def asnyc_write_file(filepath, mode, text):
    async with aiofiles.open(filepath, mode) as f:
        await f.write(text)

# TODO is it still needed?
def write_event_received(text=str):
    pass
flashcounter =0
def update_flash_counter(text=str):
    global flashcounter
    flashcounter +=1
    write_file(os.getenv("FLASH_COUNTER"), "w", str(flashcounter))

def write_bait_counter(text=str):
    filename = os.getenv("BAIT_COUNTER_FILE", "BAIT_HISTORX_FILE")
    write_file(filename,"w", text)

def write_snaman_file(text=str):
    write_file(os.getenv("OBS_OVERLAY_SNAMAN_FILE"), "w", text)

def bait_quotes_array():
    with open(os.getenv("BAIT_QUOTES_FILE"), "r", encoding="utf-8") as f:
        x =f.readlines()
    f.close()
    return x

def write_screenkey_timer(text=str):
   write_file(os.getenv("OBS_OVERLAY_SCREENKEY_TXT"), "w", text)

def write_snaalert_file(text=str):
    write_file (os.getenv("OBS_OVERLAY_SNAALARM_TXT"),"w", text)

def write_top_baiter(text=str):
    write_file(os.getenv("OBS_OVERLAY_TOPBAITER_TXT"), "w", text)

def write_score_chart_values(values):
    with open (os.getenv("HTML_OVERLAY_CHART_VALUES"), "w") as f:
        f.write("[\n")
        f.write("  " + values[0] + ",\n")
        f.write("  " + json.dumps(values[1], ensure_ascii=False, indent=2) + ",\n")
        f.write("  " + json.dumps(values[2], ensure_ascii=False, indent=2) + ",\n")
        f.write("  " + values[3]+",\n")
        f.write("  " + values[4]+",\n")
        f.write("  " + values[5] + ",\n")
        f.write("  " + values[6] + ",\n")
        f.write("  " + values[7] + "\n")
        f.write("]\n")
        #"""

def update_vip_fishing_chart(vals):
    # name, points, img
    values = vals[0]
    imgs = vals[1]
    with open (os.getenv("HTML_OVERLAY_BAIT_PODIUM"), "w") as f:
        f.write("[\n")
        result = ",\n".join([f'{{ "name": "{k}", "points": {v}, "img": "{imgs[k]}" }}' for k, v in values.items()])
        print(result)
        f.write(result)
        f.write("]\n")
