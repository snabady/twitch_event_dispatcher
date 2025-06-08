
event_map= {
}


def blub():
    raise NotImplementedError()

def register_event_source(event_name):
    if event_name not in event_map:
        event_map[event_name] = []

def register_handler(event_name, handler):
    if event_name not in event_map:
        register_event_source(event_name)
    event_map[event_name].append(handler)
    
def dispatch_event(event_name, data) -> str:
    if event_name not in event_map:
        raise ValueError (f"{event_name} not registered. could not dispatch")
    if not event_map[event_name]:
        raise ValueError( f"no handler registered for {event_name}")
    return f"successfully dispatched {event_name}"
    