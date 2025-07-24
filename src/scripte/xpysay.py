from Xlib import X, display, Xutil, Xatom
from Xlib.ext import randr
from PIL import Image, ImageSequence
import time
import sys

def create_argb_window(disp, width, height, x=100, y=100):
    screen = disp.screen()
    root = screen.root

    # Find ARGB visual (for transparency)
    visual = None
    for v in screen.allowed_depths:
        for vis in v.visuals:
            if v.depth == 32:
                visual = vis
                break
    if not visual:
        visual = root.get_visual()

    # Create window
    win = root.create_window(
        x, y, width, height,
        0, visual.visual_id,
        X.InputOutput,
        visual.visual_id,
        background_pixel=0x00000000,  # transparent
        event_mask=X.ExposureMask,
        colormap = root.create_colormap(X.AllocNone, visual.visual_id),
        override_redirect=True,
    )
    win.map()
    return win

def show_gif_on_window(win, disp, gif_path):
    im = Image.open(gif_path)
    frames = [frame.copy().convert('RGBA') for frame in ImageSequence.Iterator(im)]
    delays = [frame.info.get('duration', 100) / 1000.0 for frame in ImageSequence.Iterator(im)]
    gc = win.create_gc()
    width, height = im.size

    while True:
        for idx, frame in enumerate(frames):
            # Convert PIL image to raw bytes
            data = frame.tobytes("raw", "BGRA")
            # Create XImage
            ximage = disp.create_image(
                                width, height, 32, X.ZPixmap, data, width * 4
                            )
            win.put_image(gc, ximage, 0, 0, 0, 0, width, height)
            disp.flush()
            time.sleep(delays[idx])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gif_on_desktop_x11.py <gif_path>")
        sys.exit(1)
    gif_path = sys.argv[1]
    disp = display.Display()
    im = Image.open(gif_path)
    width, height = im.size
    win = create_argb_window(disp, width, height)
    show_gif_on_window(win, disp, gif_path)