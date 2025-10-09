#!/usr/bin/env python3
"""
view_frame_ascii.py

Terminal-ASCII/ANSI previewer für rohe RGB24-Binärdateien, die im
"segment-wise" Layout gepackt sind (wie die von send_ddp.py erzeugten Dateien).

Features:
- Rekonstruiert Bild aus bytes nach: segments x segment_width, height=8
- Unterstützt serpentine (zig-zag) und color_order (RGB / GRB)
- Gibt eine farbige Terminal-Vorschau mit 24-bit ANSI-Hintergrundfarben aus
- Alternativ reines ASCII (--no-color) mit '██' / '  ' oder customizable chars
- Skaliert horizontal via --scale (n Spalten pro Pixel) für bessere Lesbarkeit

Beispiel:
  python3 view_frame_ascii.py frame.bin --segments 4 --segment-width 24 --serpentine --color-order GRB
  python3 view_frame_ascii.py frame.bin --no-color --scale 2

Hinweis: Terminal muss ANSI 24-bit Farben unterstützen (most modern terminals do).
"""
import argparse
import os
import sys

HEIGHT = 8

CSI = "\x1b["

def parse_args():
    p = argparse.ArgumentParser(description="Terminal ASCII/ANSI preview for raw RGB24 frame (segment layout).")
    p.add_argument("file", help="input binary file (raw RGB bytes)")
    p.add_argument("--segments", type=int, default=4, help="Anzahl Segmente / Datenleitungen (default: 4)")
    p.add_argument("--segment-width", type=int, default=24, help="Breite eines Segments in Pixel (default: 24)")
    p.add_argument("--serpentine", action="store_true", help="Wenn gesetzt: jede ungerade Zeile ist rückwärts geordnet")
    p.add_argument("--color-order", choices=["RGB","GRB"], default="RGB", help="Farbkanalreihenfolge in Datei (default: RGB)")
    p.add_argument("--no-color", action="store_true", help="Keine ANSI-Farben verwenden (ASCII only)")
    p.add_argument("--on-char", default="██", help="Zeichen für 'on' Pixel im no-color Modus (default: '██')")
    p.add_argument("--off-char", default="  ", help="Zeichen für 'off' Pixel im no-color Modus (default: two spaces)")
    p.add_argument("--scale", type=int, default=1, help="Horizontaler Skalierungsfaktor (Default: 1)")
    return p.parse_args()

def map_incoming_to_rgb(b0, b1, b2, order):
    if order.upper() == "RGB":
        return (b0, b1, b2)
    if order.upper() == "GRB":
        return (b1, b0, b2)
    return (b0, b1, b2)

def build_matrix_from_bytes(data: bytes, segments: int, seg_width: int, serpentine: bool, color_order: str):
    total_w = segments * seg_width
    expected = total_w * HEIGHT * 3
    if len(data) != expected:
        raise ValueError(f"Dateigröße {len(data)} bytes stimmt nicht mit erwartetem {expected} bytes.\n"
                         f"segments={segments}, segment_width={seg_width}, height={HEIGHT} => expected {expected}")
    # create a matrix width x height of (r,g,b)
    matrix = [[(0,0,0) for _ in range(total_w)] for _ in range(HEIGHT)]
    idx = 0
    for seg in range(segments):
        seg_x0 = seg * seg_width
        for y in range(HEIGHT):
            if serpentine and (y % 2 == 1):
                x_iter = range(seg_x0 + seg_width - 1, seg_x0 - 1, -1)
            else:
                x_iter = range(seg_x0, seg_x0 + seg_width)
            for gx in x_iter:
                b0 = data[idx]; b1 = data[idx+1]; b2 = data[idx+2]
                idx += 3
                r,g,b = map_incoming_to_rgb(b0, b1, b2, color_order)
                matrix[y][gx] = (r,g,b)
    return matrix

def rgb_to_ansi_bg(r,g,b):
    # background color
    return f"{CSI}48;2;{r};{g};{b}m"

def reset_ansi():
    return f"{CSI}0m"

def luminosity(r,g,b):
    # simple perceived brightness
    return 0.2126*r + 0.7152*g + 0.0722*b

def print_matrix_ansi(matrix, scale=1, no_color=False, on_char="██", off_char="  "):
    height = len(matrix)
    width = len(matrix[0]) if height>0 else 0
    for y in range(height):
        line = []
        for x in range(width):
            r,g,b = matrix[y][x]
            if no_color:
                # decide on/off by brightness threshold
                bright = luminosity(r,g,b)
                if bright > 16:  # small threshold
                    ch = on_char * scale
                else:
                    ch = off_char * scale
                line.append(ch)
            else:
                # use ANSI background color and print spaces (scaled)
                bg = rgb_to_ansi_bg(r,g,b)
                reset = reset_ansi()
                # use two spaces per pixel (or more with scale)
                block = " " * (2 * scale)
                line.append(f"{bg}{block}{reset}")
        sys.stdout.write("".join(line) + "\n")
    sys.stdout.flush()

def main():
    args = parse_args()
    if not os.path.isfile(args.file):
        print("Datei nicht gefunden:", args.file, file=sys.stderr)
        sys.exit(2)
    with open(args.file, "rb") as f:
        data = f.read()
    try:
        matrix = build_matrix_from_bytes(data, args.segments, args.segment_width, args.serpentine, args.color_order)
    except ValueError as e:
        print("Fehler:", e, file=sys.stderr)
        sys.exit(3)
    # print header
    total_w = args.segments * args.segment_width
    print(f"Preview {args.file}: {total_w}x{HEIGHT}  segments={args.segments}, seg_width={args.segment_width}, serpentine={args.serpentine}, color_order={args.color_order}")
    print("(Use --no-color for ASCII only)")
    print_matrix_ansi(matrix, scale=args.scale, no_color=args.no_color, on_char=args.on_char, off_char=args.off_char)

if __name__ == "__main__":
    main()
