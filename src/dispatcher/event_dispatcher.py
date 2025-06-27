from collections import defaultdict
import logging
from utils import log 
logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   

subscribers = defaultdict(list)

def subscribe_event(event_type, fn):
    logger.debug(f"registered event_type {event_type} with fkt: {fn.__name__}")
    subscribers[event_type].append(fn)

def post_event(event_type, data: str) :
    #logger.debug(f'event_type: {event_type}\nsubscribers: {subscribers}')
    if not event_type in subscribers:
        logger.debug("no subscribers registered")
        return
    for fn in subscribers[event_type]:
        logger.debug(f"dispatcher calling {fn.__name__}")
        fn(data)
