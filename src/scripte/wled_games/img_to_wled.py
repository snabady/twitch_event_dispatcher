#!/usr/bin/env python3
"""
image_to_wled_matrix.py

Convert a 2D image to a WLED-compatible raw byte stream for a 2D LED matrix and send it.

Usage:
  python image_to_wled_matrix.py IMAGE WLED_HOST WIDTH HEIGHT

Positional args:
  IMAGE       path to image file
  WLED_HOST   IP or host (optionally host:port) of your WLED device
  WIDTH       number of LEDs per row
  HEIGHT      number of LED rows

Options:
  --serpentine         Treat rows as serpentine/zig-zag (default: off)
  --start-corner STR   One of TL, TR, BL, BR (default TL)
  --color-order STR    One of RGB, GRB, BRG, RGBW (default GRB)
  --gamma FLOAT        Gamma exponent (default 1.0 = no change)
  --use-udp            Send via UDP port 21324 instead of HTTP POST
  --quiet              Minimal output

Examples:
  python image_to_wled_matrix.py picture.png 192.168.1.50 32 16 --serpentine --start-corner=TL --color-order=GRB
"""

import argparse
from PIL import Image
import requests
import socket
import sys

def parse_args():
    p = argparse.ArgumentParser(description="Send a 2D image to WLED matrix")
    p.add_argument("image", help="Image path")
    p.add_argument("wled_host", help="WLED host/IP (optionally host:port)")
    p.add_argument("width", type=int, help="Matrix width (LEDs per row)")
    p.add_argument("height", type=int, help="Matrix height (rows)")
    p.add_argument("--serpentine", action="store_true", help="Use serpentine (zig-zag) row ordering")
    p.add_argument("--start-corner", default="TL", choices=["TL","TR","BL","BR"], help="Starting corner")
    p.add_argument("--color-order", default="GRB", choices=["RGB","GRB","BRG","RGBW"], help="Color order (default GRB)")
    p.add_argument("--gamma", type=float, default=1.0, help="Gamma exponent (default 1.0)")
    p.add_argument("--use-udp", action="store_true", help="Use UDP (port 21324)")
    p.add_argument("--quiet", action="store_true", help="Less output")
    return p.parse_args()

def apply_gamma(c, gamma):
    if gamma == 1.0:
        return c
    return int((c / 255.0) ** gamma * 255 + 0.5)

def build_buffer_from_image(path, width, height, serpentine=False, start_corner="TL", color_order="GRB", gamma=1.0):
    img = Image.open(path).convert("RGB")
    img = img.resize((width, height), Image.LANCZOS)
    pixels = img.load()  # pixel access: pixels[x,y] -> (r,g,b,a?) but convert to RGB above

    bytes_per_led = 4 if color_order == "RGBW" else 3
    total_leds = width * height
    buf = bytearray(total_leds * bytes_per_led)

    # For each logical (x,y) in the target layout, compute the linear index in the strip order
    # Step 1: take the coordinate system such that start_corner maps to logical top-left
    # We will iterate y from 0..height-1 and x from 0..width-1 in logical top-left orientation,
    # then transform if the chosen corner requires flipping.
    def transform_origin(x, y):
        # apply start_corner transform to map logical (x,y) to actual image coordinates
        # start_corner options: TL, TR, BL, BR
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
        # logical coordinates assume top-left origin after transform_origin
        lx, ly = x, y
        # serpentine alternates the direction of every other row
        if serpentine and (ly % 2 == 1):
            lx = width - 1 - lx
        return ly * width + lx

    # Build mapping: for each logical y,x compute source image pixel coordinates, apply gamma & color order
    for y in range(height):
        for x in range(width):
            # map logical to image coordinates depending on start_corner
            img_x, img_y = transform_origin(x, y)
            # PIL pixel coordinate is (x, y) with origin top-left of image we resized to width,height
            r, g, b = pixels[img_x, img_y][:3]
            if gamma != 1.0:
                r = apply_gamma(r, gamma)
                g = apply_gamma(g, gamma)
                b = apply_gamma(b, gamma)

            idx = linear_index_from_logical(x, y)
            base = idx * bytes_per_led

            if color_order == "RGBW":
                # naive white extraction: W = min(R,G,B), remainder to RGB channels
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
    try:
        payload = build_buffer_from_image(args.image, args.width, args.height, serpentine=args.serpentine, start_corner=args.start_corner, color_order=args.color_order, gamma=args.gamma)
    except Exception as e:
        print("Error building buffer:", e)
        sys.exit(2)

    if not args.quiet:
        print(f"Built {len(payload)} bytes ({len(payload)//(4 if args.color_order=='RGBW' else 3)} LEDs)")

    try:
        if args.use_udp:
            if not args.quiet:
                print(f"Sending {len(payload)} bytes via UDP to {args.wled_host}:21324")
            send_udp(args.wled_host, payload)
            if not args.quiet:
                print("UDP send complete.")
        else:
            if not args.quiet:
                print(f"POSTing payload to http://{args.wled_host}/win")
            r = send_http(args.wled_host, payload)
            if not args.quiet:
                print("HTTP response:", r.status_code)
    except Exception as e:
        print("Error sending payload:", e)
        sys.exit(3)

if __name__ == "__main__":
    main()
