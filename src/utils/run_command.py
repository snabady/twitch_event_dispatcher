import asyncio
import subprocess
from threading import Thread



class GatherTasks():
    def __init__(self):
        self.task_list = []

    def add_task(self, fn):
        self.task_list.append(fn)

    def run_tasks(self):
        
        for task in self.task_list:
            t = Thread(target=task)
            t.start()    
            t.join()

async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_shell(
                            cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )

    tdout, stderr = await process.communicate()
    print(f"stdout: {tdout}")

def run_mpv(filepath: str,  volume: str , no_video=False):
    #
    #""
    volume = "--volume="+str(volume)
    subprocess.Popen(['mpv', '--no-video=', str(no_video) ,volume,filepath])


def run_xcowsay(image:str , text: str, time: int, monitor:int):
    
    cow_time  = f"--time={str(time)}"
    monitor = f'--monitor={str(monitor)}'
    subprocess.Popen(['xcowsay', text , "--image" , image, '--think', monitor , cow_time])
    
#run_xcowsay("/home/sna/5n4fu_stream/media/img/sna.png", "blub" , 20, 1)
#run_mpv(True, 120, "/home/sna/5n4fu_stream/media/alerts/new_follower.mp3" )
#run_mpv( "/home/sna/5n4fu_stream/media/alerts/new_follower.mp3" , 120, True)

