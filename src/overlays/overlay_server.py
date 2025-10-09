import os

from fastapi import FastAPI, WebSocket,Query
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/event_board", StaticFiles(directory="/home/sna/5n4fu_stream/event_board/", html=True), name="event_board")
app.mount("/vip_chart", StaticFiles(directory="/home/sna/src/twitch/src/test/siegerehrung", html=True), name="vip_chart")

app.mount("/ending_screen", StaticFiles(directory="/home/sna/5n4fu_stream/ending_screen/", html=True), name="ending_screen")



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await webwocket.receive_text()
            print("server got: ", data)
            await websocket.send_text(f"Server received: {data}")
    except Exception as e:
        print("[server] client disconnected", e)

@app.get("/")
def index():
    return {
        "overlays": [
            "/event_board",
            "/vip_chart",
            "/ending_screen",
        ]
    }


@app.get("/event_board/play")
def play_sound(sound: str = Query(...)):
    # Absoluter Pfad zu deinem Overlay-Sound
    base_path = "/home/sna/5n4fu_stream/event_board/sounds/"
    file_path = os.path.join(base_path, sound)

    if os.path.isfile(file_path):
        return FileResponse(file_path, media_type="audio/webm")
    else:
        return {"error": f"File not found: {file_path}"}
