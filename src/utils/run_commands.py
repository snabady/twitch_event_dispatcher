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
