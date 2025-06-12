import asyncio
import subprocess

async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_shell(
                            cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )

    tdout, stderr = await process.communicate()
    print(f"stdout: {tdout}")

def run_mpv(filepath: str,  volume: str , no_video=False,):
    subprocess.Popen(W
        ['mpv', '--no-video', '--volume=120', '/home/sna/src/scripte_twitch/audio/blub.mp3'],
    )


#run_mpv('/home/sna/src/scripte_twitch/audio/blub.mp3', 150, no_video=True)