#!/usr/bin/env python3
"""
send_text_ddp_local.py

- Rendert festen Text in 8x72 Pixel (keine Lauftext).
- Farbe: pink (RGB 255,0,255).
- Keine serpentine Verdrahtung.
- Erzeugt eine rohe RGB24 Datei "frame_raw.bin" (72*8*3 = 1728 B).
- Optional: versucht ddpsend.py (externes Tool) aufzurufen, wenn vorhanden.
"""

from PIL import Image, ImageDraw, ImageFont
import shutil
import subprocess
import sys
import os

WIDTH = 72
HEIGHT = 8
FG_COLOR = (255, 0, 255)  # pink / magenta
BG_COLOR = (0, 0, 0)
DDP_IP = "192.168.0.6"
DDP_PORT = 4048
OUT_FILENAME = "frame_raw.bin"

def render_text_bitmap(text: str, font_path=None):
    # Versuche eine kleine 8px-TTF, sonst default font (meist 8px hoch)
    if font_path and os.path.exists(font_path):
        font = ImageFont.truetype(font_path, 8)
    else:
        font = ImageFont.load_default()

    # Ermittle Textbreite
    text_width, text_height = font.getsize(text)
    # Neues Bild mit Höhe 8, Breite min(text_width, WIDTH)
    img = Image.new("L", (max(text_width, 1), HEIGHT), 0)
    draw = ImageDraw.Draw(img)
    # Vertikal zentrieren
    y = max(0, (HEIGHT - text_height) // 2)
    draw.text((0, y), text, fill=255, font=font)

    # Falls breiter als WIDTH, abschneiden (kein Lauftext)
    if img.width > WIDTH:
        img = img.crop((0, 0, WIDTH, HEIGHT))
    # Falls schmaler: linksbündig in ein WIDTH-Bild einfügen
    if img.width < WIDTH:
        full = Image.new("L", (WIDTH, HEIGHT), 0)
        full.paste(img, (0, 0))
        img = full

    return img

def bitmap_to_rgb_bytes(img, fg_color=FG_COLOR, bg_color=BG_COLOR):
    # Thresholden auf 1-Bit
    bw = img.point(lambda p: 255 if p > 128 else 0, '1')
    pixels = bw.load()
    out = bytearray()
    # Keine serpentine: Zeilen von oben nach unten, Spalten von links nach rechts
    for y in range(HEIGHT):
        for x in range(WIDTH):
            on = pixels[x, y]
            if on:
                out.extend(bytes(fg_color))
            else:
                out.extend(bytes(bg_color))
    return out

def save_raw_rgb(data: bytes, filename: str = OUT_FILENAME):
    with open(filename, "wb") as f:
        f.write(data)
    print(f"Wrote {len(data)} bytes to {filename} (expected {WIDTH*HEIGHT*3}).")

def try_send_with_ddpsend(filename: str, ip: str = DDP_IP, port: int = DDP_PORT):
    """
    Versucht ein externes Tool ddpsend.py (oder ddpsend) zu finden und aufzurufen.
    ddpsend.py (aus ddptools) akzeptiert typischerweise: ddpsend.py <ip> <port> <file>
    Falls nicht vorhanden, gibt das Skript Hinweise zum manuellen Senden.
    """
    # Suche nach ausführbarem ddpsend in PATH
    finder = shutil.which("ddpsend") or shutil.which("ddpsend.py")
    if finder:
        cmd = [finder, ip, str(port), filename]
        print("Found ddpsend executable at:", finder)
        print("Calling:", " ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
            print("DDP send finished (via ddpsend).")
        except subprocess.CalledProcessError as e:
            print("ddpsend failed:", e)
    else:
        print()
        print("Kein ddpsend im PATH gefunden.")
        print("Beispiel, wie du die Datei mit dem ddptools ddpsend.py senden kannst:")
        print("  git clone https://github.com/cdeletre/ddptools.git")
        print("  python3 ddptools/ddpsend.py 127.0.0.1 4048", filename)
        print("Oder installiere/verwende ein anderes DDP-Tool, das rohe RGB24-Dateien sendet.")
        print()

def main():
    text = "HALLO"  # Beispieltext, anpassen
    print("Render text to 8x72 bitmap:", text)
    img = render_text_bitmap(text)
    rgb = bitmap_to_rgb_bytes(img)
    save_raw_rgb(rgb, OUT_FILENAME)
    # Versuche zu senden (optional)
    try_send_with_ddpsend(OUT_FILENAME)

if __name__ == "__main__":
    main()
