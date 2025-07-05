def write_file(filepath=str, mode= str , text= str):
    with open(filepath, mode) as f:
        f.write(text)
    


async def asnyc_write_file(filepath, mode, text):
    async with aiofiles.open(filepath, mode) as f:
        await f.write(text)
