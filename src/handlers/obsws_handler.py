import logging
from src.utils import log

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   



def handle_twitch_streaminfo_event(event: dict):
 
    logger.debug("IN handle_twitch_streaminfo_event")
    fn = event_types.get(event.get("event_type"))
    logger.debug(f'{fn.__name__}')
    fn(event)


def handle_stream_online(event):
    # -> DB startdate
    # -> start-playlist
    # -> TEXT-Overlay obs values adjustment
    # streamtitle? category?
    # 
    logger.debug(f"in: handle_stream_online")



def handle_stream_offline(event):
    logger.debug(f"in: handle_stream_offline")


def handle_channel_update_v2(event):
    logger.debug(f"in: handle_chanel_update_v2")


def handle_channel_update(event):
    logger.debug(f"in: handle_channel_update")


event_types = {
            "stream.online": handle_stream_online,
            "stream.offline": handle_stream_offline,
            "channel.update_v2": handle_channel_update_v2,
            "channel.update": handle_channel_update
        }
