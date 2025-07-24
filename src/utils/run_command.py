import asyncio
import subprocess
import queue
import logging
import re
from threading import Thread
import threading
from utils import log
from num2words import num2words

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   
tts_wav_filepath ="/home/sna/5n4fu_stream/media/tts_wav/run_command.wav"

class EventQueue:

    def __init__(self):
        self.logger = logging.getLogger("EVENTQUEUE")
        self.cmdpr = log.add_logger_handler(self.logger)
        self.cmdpr.setLevel(logging.DEBUG) 
        self.taskqueue = queue.Queue()
        self.thread_worker = threading.Thread(target=self.dequeue, daemon=True)
        self.running = True
        self.thread_worker.start()
        
    def enqueue(self, event):
        self.cmdpr.info(f'enquue: {event}')
        self.taskqueue.put(event)

    def dequeue( self ):
        
        while self.running:
            #self.taskqueue.qsize()
            task = self.taskqueue.get()
            self.cmdpr.debug(f'type (task) {type(task)} ')
            self.cmdpr.info(f'queue-size: {self.taskqueue.qsize()}')
            if task == None:
                break
            task()
        self.taskqueue.task_done() 
  
class GatherTasks():
    def __init__(self): 
        self.task_list = []

    def add_task(self, fn):
        self.task_list.append(fn)

    def run_tasks(self):
        threads = []
        for task in self.task_list:
            t = Thread(target=task)
            t.start() 
            threads.append(t)   
            
        for t in threads: 
            t.join()

class EventTimer:
    def __init__(self, interval, callback, *args, **kwargs):
        self.interval = interval
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.thread = None

    def start(self):
        self.thread = threading.Timer(self.interval, self.callback, self.args, self.kwargs)
        self.thread.start()


async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_shell(
                            cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )

    tdout, stderr = await process.communicate()
    #logger.info(f"stdout: {tdout}")

def run_mpv(filepath: str,  volume: str , no_video=False):
    
    #    no_vid = f"--no-video"
    #volume = "--volume="+str(volume)
    #if no_vid:
    #    subprocess.run(['mpv', no_vid,volume,filepath])
    #else:
    subprocess.run(['mpv', filepath])


def run_xcowsay(image:str , text: str, time: int, monitor:int, block=True):
    
    cow_time  = f"--time={str(time)}"
    monitor = f'--monitor={str(monitor)}'
    if block:
        subprocess.run(['xcowsay', text , "--image" , image, '--think', monitor , cow_time])
    else:    
        subprocess.Popen(['xcowsay', text , "--image" , image, '--think', monitor , cow_time])


def run_tts(text:str):
    numbers = re.findall(r'-?\d+', text)
    logger.debug(numbers)
    for num in numbers:
        num_str = num2words(num, lang='de')
        text = text.replace(num, num_str, 1)
    
    text = text.replace("!tts", "", 1)
    logger.debug(f"tts_text: {text}")
    subprocess.run(["tts", "--text", text, "--model_name", "tts_models/de/css10/vits-neon", "--out_path", tts_wav_filepath])
    subprocess.run(["mpv" , tts_wav_filepath])
    
def create_toilet_file(filepath: str, font: str, text: str):
    
    result = subprocess.run(['toilet', text, '-w 100', '-f', font  ],
    stdout=subprocess.PIPE, 
    text=True)
    with open (filepath, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    
#run_xcowsay("/home/sna/5n4fu_stream/media/img/sna.png", "blub" , 20, 1)
#run_mpv(True, 120, "/home/sna/5n4fu_stream/media/alerts/new_follower.mp3" )
#run_mpv( "/home/sna/5n4fu_stream/media/alerts/new_follower.mp3" , 120, True)

