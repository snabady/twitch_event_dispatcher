import time
from dispatcher.event_dispatcher import post_event
from emotes.display import start_emote_display

def example_trigger():
    url = "https://cdn.7tv.app/emote/01F6VRNNM00002CGDRZACE6MYQ/2x.avif"
    post_event("got_7tv_image", url)

if __name__ == "__main__":
    start_emote_display()
    time.sleep(2)  # Wait for display thread to start

    # Trigger emote event from anywhere
    example_trigger()

    # Keep main thread alive
    while True:
        time.sleep(1)