from collections import defaultdict
import logging
from utils import log 
logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.INFO)   

subscribers = defaultdict(list)

def subscribe_event(event_type, fn):
    logger.debug(f"registered event_type {event_type} with fkt: {fn.__name__}")
    subscribers[event_type].append(fn)

def get_handlers(event_name):
    """Retrieve all handlers for a given event name."""
    return _event_handlers.get(event_name, [])

def post_event(event_type, data) :
    #logger.debug(f'event_type: {event_type}\nsubscribers: {subscribers}')
    if not event_type in subscribers:
        logger.debug(f"no subscribers registered for event_type {event_type}")
        return
    results = []
    for fn in subscribers[event_type]:
        logger.debug(f"dispatcher calling {fn.__name__}")
        result = fn(data)
        results.append(result)
    return result
