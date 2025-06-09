from collections import defaultdict

subscribers = defaultdict(list)

def blub():
    raise NotImplementedError()

def subscribe_event(event_type:str, fn):
    subscribers[event_type].append(fn)

def post_event(event_type, data: str) :
    if not event_type in subscribers:
        print("no subscribers registered")
        return
    for fn in subscribers[event_type]:
        print(f"calling {fn.__name__}")
        fn(data)
    
    