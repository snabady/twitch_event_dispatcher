#run_mpv('/home/sna/src/scripte_twitch/audio/blub.mp3', 150, no_video=True)

def handle_channel_cheer(event: dict ):
    event_data = event.get("event_data")
    
    print(f"EVENT_DATA: {event_data}")
    raise NotImplementedError
def handle_channel_follow(event: dict):
    event_data = event.get("event_data")
    print(f"EVENT_DATA: {event_data}")
    raise NotImplementedError
def hanlde_channel_raid(event: dict):
    event_data = event.get("event_data")
    print(f"EVENT_DATA: {event_data}")
    raise NotImplementedError