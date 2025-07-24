import threading
import time
from dispatcher.event_dispatcher import post_event, subscribe_event

class MultiTimerClass:
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # state: {event_name: {"remaining": int, "thread": Thread, "active": bool, "event_data": dict}}
        self.timers = {}
        self.lock = threading.Lock()

        subscribe_event("timer_start_event", self.handle_start_event)
        subscribe_event("timer_increase_event", self.handle_increase_event)
        subscribe_event("timer_status_event", self.handle_status_query)

    def handle_start_event(self, data):
        event_name = data.get("event_name")
        duration = data.get("duration", 0)
        event_data = data.get("event_data", {})
        if not event_name:
            return

        with self.lock:
            # If a timer with this name exists, stop it
            if event_name in self.timers and self.timers[event_name]["active"]:
                self.timers[event_name]["active"] = False  # Will stop existing thread

            # Start new timer
            self.timers[event_name] = {
                "remaining": duration,
                "active": True,
                "event_data": event_data,
                "thread": threading.Thread(target=self._run_timer, args=(event_name,), daemon=True)
            }
            self.timers[event_name]["thread"].start()

    def handle_increase_event(self, data):
        event_name = data.get("event_name")
        increase = data.get("increase", 0)
        if not event_name or increase <= 0:
            return

        with self.lock:
            if event_name in self.timers and self.timers[event_name]["active"]:
                self.timers[event_name]["remaining"] += increase

    def handle_status_query(self, data):
        event_name = data.get("event_name")
        if not event_name:
            return

        with self.lock:
            if event_name in self.timers:
                timer = self.timers[event_name]
                status = "running" if timer["active"] else "stopped"
                post_event("timer_status_event", {
                    "event_name": event_name,
                    "event_data": timer["event_data"],
                    "remaining": timer["remaining"],
                    "status": status
                })
            else:
                post_event("timer_status_event", {
                    "event_name": event_name,
                    "event_data": {},
                    "remaining": 0,
                    "status": "not_found"
                })

    def _run_timer(self, event_name):
        while True:
            with self.lock:
                timer = self.timers.get(event_name)
                if not timer or not timer["active"]:
                    break
                if timer["remaining"] <= 0:
                    timer["active"] = False
                    post_event("timer_done_event", {
                        "event_name": event_name,
                        "event_data": timer["event_data"],
                        "status": "done"
                    })
                    break
                timer["remaining"] -= 1
            time.sleep(1)

# Usage: instantiate once
multi_timer = MultiTimerClass()
