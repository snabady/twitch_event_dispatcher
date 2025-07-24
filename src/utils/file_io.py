def write_file(filepath=str, mode= str , text= str):
    with open(filepath, mode) as f:
        f.write(text)

async def asnyc_write_file(filepath, mode, text):
    async with aiofiles.open(filepath, mode) as f:
        await f.write(text)

def write_event_received(text=str):
    write_file("/home/sna/5n4fu_stream/data/sna_events.txt", "a", text)

def update_flash_counter(text=str):
    write_file("/home/sna/5n4fu_stream/data/sna_flash_counter.txt", "w", text)

def write_bait_counter(text=str):
    write_file("/home/sna/5n4fu_stream/data/baitgame/bait_counter.txt", "w", text)

def write_snaman_file(text=str):
    write_file("/home/sna/5n4fu_stream/obs_files/snaman.txt", "w", text)


def bait_quotes_array():
    with open("/home/sna/src/twitch/src/baitgame/data/bait_quotes.txt", "r", encoding="utf-8") as f:
        x =f.readlines()
        #print(x)
        
    f.close()
    print (type(x))
    print(len(x))
    return x

def write_screenkey_timer(text=str):
   write_file("/home/sna/5n4fu_stream/data/timer/screenkey.txt", "w", text)


def write_snaalert_file(text=str):
    write_file ("/home/sna/5n4fu_stream/data/snaalarm.txt","w", text)


def write_top_baiter(text=str):
    write_file("/home/sna/5nafu_stream/data/bait/topbaiter.txt", "w", text)
