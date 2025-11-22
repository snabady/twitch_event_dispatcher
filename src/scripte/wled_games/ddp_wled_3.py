#!/usr/bin/env python3
"""
send_ddp.py

Erzeugt aus Text ein 8px-hohes Bitmap für ein LED-Layout mit mehreren Segmenten
(typisch: 4 Datapins / 4 Segmente × 24 = 96×8) und sendet das rohe RGB24-Frame
per DDP an ein WLED (via externes ddpsend.py/ddpsend).

Warum so: viele DDP-Tools (z.B. ddptools/ddpsend.py) bauen Header und Fragmentierung
korrekt. Dieses Skript rendert und packt die Pixel in der richtigen Reihenfolge
(unterstützt serpentine & GRB) und ruft dann das vorhandene ddpsend auf.

Benutzung:
  pip install pillow
  git clone https://github.com/cdeletre/ddptools.git   # falls du ddpsend.py noch nicht hast
  python3 send_ddp.py --text HALLO --ip 192.168.1.50 --port 4048

Optionen:
  --text            Text, der gerendert werden soll
  --ip              Ziel-IP (WLED), default 127.0.0.1
  --port            Ziel-Port (DDP), default 4048
  --segments        Anzahl Segmente / Datenleitungen, default 4
  --segment-width   Breite eines Segments in Pixel, default 24
  --serpentine      true/false, default false
  --color-order     RGB oder GRB, default RGB
  --font            Pfad zu einer TTF-Font (optional)
  --no-send         nur Frame schreiben, nicht senden (für Debug)
"""
from PIL import Image, ImageDraw, ImageFont
import argparse, tempfile, shutil, subprocess, os, sys

DEFAULT_IP = "192.168.0.6"
DEFAULT_PORT = 4048
DEFAULT_SEGMENTS = 4
DEFAULT_SEGMENT_WIDTH = 24
HEIGHT = 8
FG_COLOR = (255, 0, 255)  # pink
BG_COLOR = (0, 0, 0)

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

def render_text_bitmap(text: str, total_width: int, font_path=None):
    if font_path and os.path.exists(font_path):
        font = ImageFont.truetype(font_path, 8)
    else:
        font = ImageFont.load_default()

    text_w, text_h = measure_text(text, font)
    img = Image.new("L", (max(text_w, 1), HEIGHT), 0)
    draw = ImageDraw.Draw(img)
    y = max(0, (HEIGHT - text_h) // 2)
    draw.text((0, y), text, fill=255, font=font)

    # Crop or pad to total_width
    if img.width > total_width:
        img = img.crop((0, 0, total_width, HEIGHT))
    elif img.width < total_width:
        full = Image.new("L", (total_width, HEIGHT), 0)
        full.paste(img, (0,0))
        img = full
    return img

def map_color_order(rgb_tuple, order):
    r,g,b = rgb_tuple
    if order.upper() == "RGB":
        return (r,g,b)
    if order.upper() == "GRB":
        return (g,r,b)
    return (r,g,b)

def bitmap_to_rgb_bytes(img, segments, seg_width, serpentine, color_order, fg=FG_COLOR, bg=BG_COLOR):
    bw = img.point(lambda p: 255 if p > 128 else 0, '1')
    pixels = bw.load()
    out = bytearray()
    total_w = segments * seg_width

    for seg in range(segments):
        seg_x0 = seg * seg_width
        for y in range(HEIGHT):
            if serpentine and (y % 2 == 1):
                x_iter = range(seg_x0 + seg_width - 1, seg_x0 - 1, -1)
            else:
                x_iter = range(seg_x0, seg_x0 + seg_width)
            for gx in x_iter:
                on = pixels[gx, y]
                packed = map_color_order(fg if on else bg, color_order)
                out.extend(bytes(packed))
    return out

def call_ddpsend_bin(binfile, ip, port):
    # Suche nach ddpsend(/ddpsend.py) im PATH
    finder = shutil.which("ddpsend") or shutil.which("ddpsend.py")
    if not finder:
        return False, ("ddpsend nicht gefunden. Bitte ddpsend.py aus ddptools in PATH legen.\n"
                       "Beispiel: git clone https://github.com/cdeletre/ddptools.git\n"
                       "Dann: python3 ddptools/ddpsend.py {ip} {port} {file}")
    cmd = [finder, ip, str(port), binfile]
    try:
        subprocess.run(cmd, check=True)
        return True, f"ddpsend ausgeführt: {finder}"
    except subprocess.CalledProcessError as e:
        return False, f"ddpsend fehlgeschlagen: {e}"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--text", required=True)
    p.add_argument("--ip", default=DEFAULT_IP)
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--segments", type=int, default=DEFAULT_SEGMENTS)
    p.add_argument("--segment-width", type=int, default=DEFAULT_SEGMENT_WIDTH)
    p.add_argument("--serpentine", action="store_true")
    p.add_argument("--color-order", choices=["RGB","GRB"], default="RGB")
    p.add_argument("--font", default=None)
    p.add_argument("--no-send", action="store_true", help="Nur Datei erzeugen, nicht senden")
    args = p.parse_args()

    total_w = args.segments * args.segment_width
    img = render_text_bitmap(args.text, total_w, font_path=args.font)
    rgb = bitmap_to_rgb_bytes(img, args.segments, args.segment_width, args.serpentine, args.color_order)

    expected = args.segments * args.segment_width * HEIGHT * 3
    if len(rgb) != expected:
        print("Fehler: erzeugte Bytes stimmen nicht mit erwarteter Größe überein.", file=sys.stderr)
        print(f"Erwartet {expected}, erzeugt {len(rgb)}", file=sys.stderr)
        sys.exit(1)

    # temporäre Datei schreiben
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tf:
        tf.write(rgb)
        tmpname = tf.name

    print(f"Frame geschrieben: {tmpname} ({len(rgb)} bytes)")

    if args.no_send:
        print("Abbruch: --no-send gesetzt. Datei bleibt erhalten.")
        return

    ok, msg = call_ddpsend_bin(tmpname, args.ip, args.port)
    print(msg)
    if not ok:
        print("Falls ddpsend nicht vorhanden ist, kannst du die Datei manuell senden:")
        print(f"  python3 ddptools/ddpsend.py {args.ip} {args.port} {tmpname}")

if __name__ == "__main__":
    main()
