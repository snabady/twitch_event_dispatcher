import sacn
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time

def wledo_text(text, WLED_IP="192.168.0.6", UNIVERSE=1, WIDTH=96, HEIGHT=8, FONT_PATH="/home/sna/Downloads/kryptonb.ttf", FONT_SIZE=12):
    # Text zu Matrix
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    image = Image.new("L", (WIDTH, HEIGHT), color=0)
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((WIDTH - w) // 2, (HEIGHT - h) // 2), text, font=font, fill=255)
    arr = np.array(image)
    arr = (arr > 128).astype(np.uint8)

    # Debug: save image
    Image.fromarray(arr * 255).save("matrix_text.png")
    print("Saved matrix_text.png")

    # In RGB umwandeln
    COLOR_ON = (0, 255, 255)   # Cyan
    COLOR_OFF = (0, 0, 0)
    pixels = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if arr[y, x]:
                pixels.append(COLOR_ON)
            else:
                pixels.append(COLOR_OFF)

    data = []
    for (r, g, b) in pixels:
        data += [r, g, b]

    sender = sacn.sACNsender()
    sender.start()
    sender.activate_output(UNIVERSE)
    sender[UNIVERSE].multicast = False
    sender[UNIVERSE].destination = WLED_IP

    # sACN DMX frames: 510 bytes (170 RGB pixels) pro Universe
    for i in range(0, len(data), 510):
        chunk = data[i: i + 510]
        u = UNIVERSE + (i // 510)
        sender.activate_output(u)
        sender[u].destination = WLED_IP
        sender[u].dmx_data = chunk + [0] * (510 - len(chunk))  # pad to 510

    time.sleep(1)
    sender.stop()
    print("Text sent!")

if __name__ == "__main__":
    # Beispiel
    wledo_text("hello SNACN :)")  # oder beliebigen Text hier eintragen
