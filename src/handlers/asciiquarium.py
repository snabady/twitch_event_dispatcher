import logging
from src.utils import log
from src.dispatcher.event_dispatcher import subscribe_event, post_event


logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   



def asciiquarium_start(event_data):
    logger.debug("asciiquarium_start func")
    post_event("obs_set_source_visibility",     { "event_data": {"scene_name":"main_view", 
                                                                 "source_name": "main_facecam", 
                                                                 "visible":False}})
    post_event ("obs_set_input_mute",           {"event_data":  {"muted":True, 
                                                                 "audiosource":"mainmic"}})
    post_event("obs_set_source_visibility",     {"event_data":  {"scene_name": "asciiquarium", 
                                                                 "source_name": "txt_brb", 
                                                                 "visible":True}})
    post_event("obs_set_source_visibility",     {"event_data":  {"scene_name": "OVERLAY_DINGE", 
                                                                 "source_name": "asciiquarium", 
                                                                 "visible":True}})
def asciiquarium_end(event_data):
    logger.debug("asciiquarium_end func")
    post_event("obs_set_source_visibility",     {"event_data":  {"scene_name": "OVERLAY_DINGE", 
                                                                 "source_name": "asciiquarium",
                                                                  "visible":False}})
    post_event("obs_set_input_mute",            { "event_data": {"muted":False, 
                                                                 "audiosource":"mainmic"}})
    post_event("obs_set_source_visibility",     {"event_data": {"scene_name": "asciiquarium", 
                                                                "source_name": "soontm", 
                                                                "visible":False}})
    post_event("obs_set_source_visibility",     {"event_data": {"scene_name": "asciiquarium", 
                                                                "source_name": "txt_brb", 
                                                                "visible":False}})
    post_event("obs_set_source_visibility",     {"event_data": {"scene_name":"main_view", 
                                                                 "source_name": "main_facecam", 
                                                                 "visible":True}})

def asciiquarium_streamstart(event_data):
    logger.debug("asciiquarium_streamstart func")
    post_event("obs_set_source_visibility",     {"event_data":  {"scene_name":"main_view", 
                                                                 "source_name": "main_facecam", 
                                                                 "visible":False}})
    post_event("obs_set_source_visibility",     {"event_data":  {"scene_name": "asciiquarium", 
                                                                 "source_name": "soontm", 
                                                                 "visible":True}})
    post_event("obs_set_source_visibility",     {"event_data":  {"scene_name": "OVERLAY_DINGE", 
                                                                 "source_name": "asciiquarium", 
                                                                 "visible":True}})
    post_event ("obs_set_input_mute",           {"event_data":  {"muted":True, 
                                                                 "audiosource":"mainmic"}})


def asciiquarium_streamend(event_data):
    # init asciiquarium ending screen
    # load stats
    # make toilet files
    # tts liest ergebnisse vor
    # 
    logger.debug("asciiquarium_streamend func")
