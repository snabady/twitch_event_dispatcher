import threading
import time
from src.dispatcher.event_dispatcher import post_event, subscribe_event
from src.utils.file_io import write_screenkey_timer
class MultiTimerClass:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.timers = {}  # {event_name: {...}}
        self.lock = threading.Lock()

        # Subscribe to events
        subscribe_event("timer_start_event", self.handle_start_event)
        subscribe_event("timer_status_event", self.handle_status_query)
        subscribe_event("timer_stop_event", self.handle_stop_event)

    def handle_start_event(self, data):
        event_name = data.get("event_name")
        duration = data.get("duration", 0)
        event_data = data.get("event_data", {})
        done_event_name = data.get("timer_done_event", "timer_done_event")  # <<<< CUSTOM EVENT NAME
        done_event_data = data.get("timer_done_event_data", "did u forget to add timer_done_event_data?")
        print(f"timeer_done_event_data: {done_event_data}")
        if not event_name:
            return

        with self.lock:
            if event_name in self.timers and self.timers[event_name]["active"]:
                # If timer exists and is active, increase duration
                self.timers[event_name]["remaining"] += duration
            else:
                # Start new timer
                self.timers[event_name] = {
                    "remaining": duration,
                    "active": True,
                    "event_data": event_data,
                    "done_event_name":done_event_name, 
                    "timer_done_event_data":done_event_data,
                    "thread": threading.Thread(target=self._run_timer, args=(event_name,), daemon=True)
                }
                self.timers[event_name]["thread"].start()

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

    def handle_stop_event(self, data):
        event_name = data.get("event_name")
        payload = data.get("payload", {})
        if not event_name:
            return

        with self.lock:
            if event_name in self.timers and self.timers[event_name]["active"]:
                self.timers[event_name]["active"] = False
                post_event("timer_stopped_event", {
                    "event_name": event_name,
                    "event_data": self.timers[event_name]["event_data"],
                    "remaining": self.timers[event_name]["remaining"],
                    "status": "stopped",
                    "payload": payload
                })
            else:
                post_event("timer_stopped_event", {
                    "event_name": event_name,
                    "event_data": {},
                    "remaining": 0,
                    "status": "not_found",
                    "payload": payload
                })

    def _run_timer(self, event_name):
        # This function runs in a separate thread per timer
        while True:
            with self.lock:
                timer = self.timers.get(event_name)
                if not timer or not timer["active"]:
                    break
                if timer["remaining"] <= 0:
                    timer["active"] = False
                    # <<<< This posts the event with the custom name
                    post_event(timer["done_event_name"],{"event_data": timer["timer_done_event_data"]})
                    break
                timer["remaining"] -= 1
                remaining = timer["remaining"]
                txt = f"{remaining//3600:02}:{remaining%3600//60:02}:{remaining%60:02}"
                write_screenkey_timer( txt)
            time.sleep(1)

