#!/usr/bin/env python3
"""
Debug/preview for sending a 2D image to WLED.

Usage example:
  python image_to_wled_matrix_debug.py picture.png 192.168.0.143 32 32 --serpentine --start-corner TL --color-order GRB

Options:
  --no-send       : do not actually send, only write payload.bin and preview_sent.png
  --use-udp       : send via UDP (21324) (default is HTTP POST to /win)
  --dump N        : print first N LED colors (default 30)
  --quiet         : less console output
"""
import argparse
from PIL import Image
import requests
import socket
import sys
import os

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("wled_host")
    p.add_argument("width", type=int)
    p.add_argument("height", type=int)
    p.add_argument("--serpentine", action="store_true")
    p.add_argument("--start-corner", default="TL", choices=["TL","TR","BL","BR"])
    p.add_argument("--color-order", default="GRB", choices=["RGB","GRB","BRG","RGBW"])
    p.add_argument("--gamma", type=float, default=1.0)
    p.add_argument("--use-udp", action="store_true")
    p.add_argument("--no-send", action="store_true", help="Don't send, just write files and preview")
    p.add_argument("--dump", type=int, default=30)
    p.add_argument("--quiet", action="store_true")
    return p.parse_args()

def apply_gamma(c, gamma):
    if gamma == 1.0:
        return c
    return int((c / 255.0) ** gamma * 255 + 0.5)

def build_buffer_from_image(path, width, height, serpentine=False, start_corner="TL", color_order="GRB", gamma=1.0):
    img = Image.open(path).convert("RGB")
    img = img.resize((width, height), Image.LANCZOS)
    pixels = img.load()
    bytes_per_led = 4 if color_order == "RGBW" else 3
    total_leds = width * height
    buf = bytearray(total_leds * bytes_per_led)

    def transform_origin(x, y):
        if start_corner == "TL":
            tx, ty = x, y
        elif start_corner == "TR":
            tx, ty = (width - 1 - x), y
        elif start_corner == "BL":
            tx, ty = x, (height - 1 - y)
        elif start_corner == "BR":
            tx, ty = (width - 1 - x), (height - 1 - y)
        else:
            tx, ty = x, y
        return tx, ty

    def linear_index_from_logical(x, y):
        lx, ly = x, y
        if serpentine and (ly % 2 == 1):
            lx = width - 1 - lx
        return ly * width + lx

    for y in range(height):
        for x in range(width):
            img_x, img_y = transform_origin(x, y)
            r, g, b = pixels[img_x, img_y][:3]
            if gamma != 1.0:
                r = apply_gamma(r, gamma)
                g = apply_gamma(g, gamma)
                b = apply_gamma(b, gamma)
            idx = linear_index_from_logical(x, y)
            base = idx * bytes_per_led

            if color_order == "RGBW":
                w = min(r, g, b)
                r2, g2, b2, w2 = max(0, r - w), max(0, g - w), max(0, b - w), w
                buf[base    ] = r2 & 0xFF
                buf[base + 1] = g2 & 0xFF
                buf[base + 2] = b2 & 0xFF
                buf[base + 3] = w2 & 0xFF
            else:
                if color_order == "RGB":
                    buf[base    ] = r & 0xFF
                    buf[base + 1] = g & 0xFF
                    buf[base + 2] = b & 0xFF
                elif color_order == "GRB":
                    buf[base    ] = g & 0xFF
                    buf[base + 1] = r & 0xFF
                    buf[base + 2] = b & 0xFF
                elif color_order == "BRG":
                    buf[base    ] = b & 0xFF
                    buf[base + 1] = r & 0xFF
                    buf[base + 2] = g & 0xFF
                else:
                    buf[base    ] = r & 0xFF
                    buf[base + 1] = g & 0xFF
                    buf[base + 2] = b & 0xFF
    return buf

def build_preview_from_buffer(buf, width, height, serpentine=False, start_corner="TL", color_order="GRB"):
    bytes_per_led = 4 if color_order == "RGBW" else 3
    total_leds = width * height
    preview = Image.new("RGB", (width, height))
    def transform_origin(x, y):
        if start_corner == "TL":
            tx, ty = x, y
        elif start_corner == "TR":
            tx, ty = (width - 1 - x), y
        elif start_corner == "BL":
            tx, ty = x, (height - 1 - y)
        elif start_corner == "BR":
            tx, ty = (width - 1 - x), (height - 1 - y)
        else:
            tx, ty = x, y
        return tx, ty
    def linear_index_from_logical(x, y):
        lx, ly = x, y
        if serpentine and (ly % 2 == 1):
            lx = width - 1 - lx
        return ly * width + lx

    for y in range(height):
        for x in range(width):
            idx = linear_index_from_logical(x, y)
            base = idx * bytes_per_led
            if base + bytes_per_led > len(buf):
                color = (0,0,0)
            else:
                if color_order == "RGBW":
                    r2 = buf[base]; g2 = buf[base+1]; b2 = buf[base+2]; w2 = buf[base+3]
                    r = min(255, r2 + w2); g = min(255, g2 + w2); b = min(255, b2 + w2)
                else:
                    if color_order == "RGB":
                        r = buf[base]; g = buf[base+1]; b = buf[base+2]
                    elif color_order == "GRB":
                        g = buf[base]; r = buf[base+1]; b = buf[base+2]
                    elif color_order == "BRG":
                        b = buf[base]; r = buf[base+1]; g = buf[base+2]
                    else:
                        r = buf[base]; g = buf[base+1]; b = buf[base+2]
                color = (int(r), int(g), int(b))
            # Put pixel at logical coordinate (x,y) — this shows the matrix as WLED will receive it
            preview.putpixel((x,y), color)
    return preview

def send_http(wled_host, payload):
    url = f"http://{wled_host}/win"
    headers = {"Content-Type": "application/octet-stream"}
    r = requests.post(url, data=payload, headers=headers, timeout=5)
    r.raise_for_status()
    return r

def send_udp(wled_host, payload, port=21324):
    host = wled_host.split(":")[0]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    sock.sendto(payload, (host, port))
    sock.close()

def main():
    args = parse_args()
    if not args.quiet:
        print(f"Building buffer from {args.image} -> {args.width}x{args.height} (serpentine={args.serpentine}, start={args.start_corner}, color={args.color_order}, gamma={args.gamma})")
    buf = build_buffer_from_image(args.image, args.width, args.height, serpentine=args.serpentine, start_corner=args.start_corner, color_order=args.color_order, gamma=args.gamma)
    total_bytes = len(buf)
    leds = total_bytes // (4 if args.color_order=="RGBW" else 3)
    if not args.quiet:
        print(f"Built {total_bytes} bytes ({leds} LEDs). Writing payload.bin and preview_sent.png")

    open("payload.bin","wb").write(buf)
    preview = build_preview_from_buffer(buf, args.width, args.height, serpentine=args.serpentine, start_corner=args.start_corner, color_order=args.color_order)
    preview.save("preview_sent.png")
    if not args.quiet:
        print("Wrote payload.bin and preview_sent.png in current directory:", os.getcwd())

    # dump first N LEDs
    bytes_per = 4 if args.color_order=="RGBW" else 3
    dump_n = min(args.dump, leds)
    print(f"First {dump_n} LEDs (index : R,G,B  / raw bytes):")
    for i in range(dump_n):
        base = i * bytes_per
        if base + bytes_per > len(buf):
            break
        if args.color_order == "RGBW":
            r2,g2,b2,w2 = buf[base],buf[base+1],buf[base+2],buf[base+3]
            r,g,b = (min(255,r2+w2), min(255,g2+w2), min(255,b2+w2))
            raw = f"{r2:02X} {g2:02X} {b2:02X} {w2:02X}"
        else:
            if args.color_order == "RGB":
                r,g,b = buf[base],buf[base+1],buf[base+2]; raw = f"{r:02X} {g:02X} {b:02X}"
            elif args.color_order == "GRB":
                g,r,b = buf[base],buf[base+1],buf[base+2]; raw = f"{g:02X} {r:02X} {b:02X}"
            elif args.color_order == "BRG":
                b,r,g = buf[base],buf[base+1],buf[base+2]; raw = f"{b:02X} {r:02X} {g:02X}"
            else:
                r,g,b = buf[base],buf[base+1],buf[base+2]; raw = f"{r:02X} {g:02X} {b:02X}"
        print(f"{i:04d} : {r:03d},{g:03d},{b:03d}  / {raw}")

    if args.no_send:
        print("No send requested (--no-send). Exiting.")
        return

    try:
        if args.use_udp:
            if not args.quiet:
                print(f"Sending {len(buf)} bytes via UDP to {args.wled_host}:21324")
            send_udp(args.wled_host, buf)
            print("UDP send complete.")
        else:
            if not args.quiet:
                print(f"POSTing payload.bin to http://{args.wled_host}/win")
            r = send_http(args.wled_host, buf)
            print("HTTP response:", r.status_code)
    except Exception as e:
        print("Error sending payload:", e)
        sys.exit(3)

if __name__ == "__main__":
    main()
