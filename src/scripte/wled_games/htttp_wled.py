#!/usr/bin/env python3
"""
ddp_http_bridge.py

Kleiner HTTP-Server (Flask) der:
- POST /display  (JSON: {"text":"HALLO"}) annimmt,
- Text in ein 8x72 Bitmap rendert (pink = (255,0,255), kein serpentine),
- eine rohe RGB24-Datei erzeugt (frame_raw.bin),
- versucht ddpsend (aus ddptools) aufzurufen, um per DDP an localhost:4048 zu senden.

Benutzung:
1) pip install pillow flask
2) (optional) git clone https://github.com/cdeletre/ddptools.git
3) python3 ddp_http_bridge.py
4) curl -X POST -H "Content-Type: application/json" -d '{"text":"HALLO"}' http://127.0.0.1:5000/display
"""
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import shutil, subprocess, os, sys, tempfile

# Panel-Größe
WIDTH = 72
HEIGHT = 8

# Farben
FG_COLOR = (255, 0, 255)   # pink / magenta
BG_COLOR = (0, 0, 0)

# DDP Ziel (das ddpsend tool wird diese IP/PORT verwenden)
DDP_IP = "127.0.0.1"
DDP_PORT = 4048

app = Flask(__name__)

def measure_text(text: str, font: ImageFont.ImageFont):
    tmp = Image.new("L", (1, 1), 0)
    draw = ImageDraw.Draw(tmp)
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except Exception:
        w, h = draw.textsize(text, font=font)
    return w, h

def render_text_bitmap(text: str, font_path=None):
    # benutze kleine 8px-TTF wenn vorhanden, sonst default
    if font_path and os.path.exists(font_path):
        font = ImageFont.truetype(font_path, 8)
    else:
        font = ImageFont.load_default()

    text_width, text_height = measure_text(text, font)
    img = Image.new("L", (max(text_width, 1), HEIGHT), 0)
    draw = ImageDraw.Draw(img)
    y = max(0, (HEIGHT - text_height) // 2)
    draw.text((0, y), text, fill=255, font=font)

    if img.width > WIDTH:
        img = img.crop((0, 0, WIDTH, HEIGHT))
    if img.width < WIDTH:
        full = Image.new("L", (WIDTH, HEIGHT), 0)
        full.paste(img, (0, 0))
        img = full
    return img

def bitmap_to_rgb_bytes(img, fg_color=FG_COLOR, bg_color=BG_COLOR):
    bw = img.point(lambda p: 255 if p > 128 else 0, '1')
    pixels = bw.load()
    out = bytearray()
    # keine serpentine: Zeilen oben->unten, Spalten links->rechts
    for y in range(HEIGHT):
        for x in range(WIDTH):
            on = pixels[x, y]
            if on:
                out.extend(bytes(fg_color))
            else:
                out.extend(bytes(bg_color))
    return out

def save_raw_rgb(data: bytes, filename: str):
    with open(filename, "wb") as f:
        f.write(data)

def call_ddpsend(file_path: str, ip: str = DDP_IP, port: int = DDP_PORT):
    # sucht ddpsend oder ddpsend.py im PATH (ddptools bietet ddpsend.py)
    finder = shutil.which("ddpsend") or shutil.which("ddpsend.py")
    if finder:
        cmd = [finder, ip, str(port), file_path]
        try:
            subprocess.run(cmd, check=True)
            return True, f"Sent via {finder}"
        except subprocess.CalledProcessError as e:
            return False, f"ddpsend failed: {e}"
    # kein ddpsend gefunden
    return False, ("ddpsend not found. Install ddptools or put ddpsend in PATH.\n"
                   "Example:\n"
                   "  git clone https://github.com/cdeletre/ddptools.git\n"
                   "  python3 ddptools/ddpsend.py 127.0.0.1 4048 frame_raw.bin")

@app.route("/display", methods=["POST"])
def display():
    """
    POST /display
    JSON body: {"text":"HALLO", "font_path":"/path/to/font.ttf"}
    Antwort: JSON mit status
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Kein Text im Request"}), 400

    font_path = data.get("font_path", None)

    img = render_text_bitmap(text, font_path=font_path)
    rgb = bitmap_to_rgb_bytes(img)

    # temporäre Datei erzeugen
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tf:
        tempname = tf.name
        tf.write(rgb)

    # Versuche ddpsend aufzurufen
    sent, msg = call_ddpsend(tempname)

    # wenn nicht gesendet, gib Info zurück (die Datei bleibt temporär)
    response = {
        "ok": sent,
        "message": msg,
        "bytes": len(rgb),
        "expected": WIDTH * HEIGHT * 3,
        "tempfile": tempname if not sent else None
    }
    return jsonify(response)

@app.route("/", methods=["GET"])
def index():
    return ("DDP HTTP bridge running. POST JSON {'text':'HALLO'} to /display\n"
            "Requires ddpsend (from ddptools) in PATH to actually send to WLED.\n"), 200

def main():
    # Hinweis
    print("Starting ddp_http_bridge on http://127.0.0.1:5000")
    print("POST JSON {'text':'HALLO'} to /display")
    app.run(host="127.0.0.1", port=5000)

if __name__ == "__main__":
    main()
