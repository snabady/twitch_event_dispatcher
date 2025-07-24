import logging
from utils import log
from dispatcher.event_dispatcher import subscribe_event, post_event


logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   



def asciiquarium_start(event_data):
    logger.debug("asciiquarium_start func")
    # main-view -> cam deactivate
    post_event("obs_set_source_visibility",{ "event_data": {"scene_name":"main_view", "source_name": "cam", "visible":False}})
    # mic-mute 
    # TODO OBS-WS request for mic
    post_event ("obs_set_input_mute", { "event_data": {"muted":True, "audiosource":"mainmic"}})
    # asciiquarium -> brb scene
    post_event("obs_set_source_visibility",{ "event_data": {"scene_name": "asciiquarium", "source_name": "txt_brb", "visible":True}})
    # asciiquarium in overlay-dinge activate
    post_event("obs_set_source_visibility", {"event_data":{"scene_name": "OVERLAY_DINGE", "source_name": "asciiquarium", "visible":True}})                                                            
    # start timer für brb seid...
    # baits in pause? -> add users to vip pool

def asciiquarium_end(event_data):
    logger.debug("asciiquarium_end func")
    # asciiquarium -> deaktivieren in overlay_dinge

    post_event("obs_set_source_visibility", {"event_data":{"scene_name": "OVERLAY_DINGE", "source_name": "asciiquarium", "visible":False}})                                                            
    # asciiquarium -> start deactivate

    post_event ("obs_set_input_mute", { "event_data": {"muted":False, "audiosource":"mainmic"}})
    post_event("obs_set_source_visibility",{ "event_data": {"scene_name": "asciiquarium", "source_name": "soontm", "visible":False}})
    post_event("obs_set_source_visibility",{ "event_data": {"scene_name": "asciiquarium", "source_name": "txt_brb", "visible":False}})
    # main-view cam an

    post_event("obs_set_source_visibility",{ "event_data": {"scene_name":"main_view", "source_name": "cam", "visible":True}})
    # brb-timer stop



def asciiquarium_streamstart(event_data):
    logger.debug("asciiquarium_streamstart func")
    # init flash-counter
    # asciiquarium -> start activate

    post_event("obs_set_source_visibility",{ "event_data": {"scene_name":"main_view", "source_name": "cam", "visible":False}})
    post_event("obs_set_source_visibility",{ "event_data": {"scene_name": "asciiquarium", "source_name": "soontm", "visible":True}})
    # overlay-dinge asciiquarium activate
    post_event("obs_set_source_visibility", {"event_data":{"scene_name": "OVERLAY_DINGE", "source_name": "asciiquarium", "visible":True}})                                                            
    # mic mute

    post_event ("obs_set_input_mute", { "event_data": {"muted":True, "audiosource":"mainmic"}})


def asciiquarium_streamend(event_data):
    # init asciiquarium ending screen
    # load stats
    # make toilet files
    # tts liest ergebnisse vor
    # 
    logger.debug("asciiquarium_streamend func")
