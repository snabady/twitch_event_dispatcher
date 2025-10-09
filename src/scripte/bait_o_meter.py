import threading
import time
from typing import Optional
from dispatcher.event_dispatcher import post_event, subscribe_event
import logging
from utils import log

class ThresholdAccumulatorSync:
    """
    Synchrone Schwellenwert-Akkumulator-Klasse.
    - Anfangswert ist 0 und erhöht sich nur durch add(n).
    - Erst beim ersten Erreichen des Schwellwerts startet der Hintergrund-Timer,
      der periodisch um decay_amount reduziert.
    - Sobald der Wert >= threshold steigt und der Cooldown vorbei ist,
      wird das Event "threshold_reached" gepostet.
    """

    def __init__(
        self,
        threshold: int,
        decay_amount: int = 1,
        decay_interval_seconds: int = 60,
        trigger_cooldown_seconds: int = 0,
        max_value: Optional[int] = None,
        total_value: int = 60,
        
    ):
        self.logger = logging.getLogger(__name__)
        self.logger = log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)

        self.threshold = threshold
        self.decay_amount = decay_amount
        self.decay_interval = decay_interval_seconds
        self.trigger_cooldown = trigger_cooldown_seconds
        self.max_value = max_value

        self.value = 0
        self.last_trigger_ts = 0.0
        subscribe_event("add_bait_led", self.add)
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._timer: Optional[threading.Timer] = None
        self._decay_started = False
        self.isfirst = False
    def start_decay(self):
        """Intern: starte den Decay-Timer, wenn er noch nicht lief."""
        if not self._decay_started:
            self._decay_started = True
            self._stop_event.clear()
            self._schedule_decay()

    def stop_decay(self):
        """Stoppe den Hintergrund-Timer komplett."""
        self._stop_event.set()
        if self._timer:
            self._timer.cancel()

    def add(self, event_data) -> int:
        """
        Erhöhe den Akkumulator um n (default 1).
        Beim ersten Überschreiten des threshold startet der Decay.
        Poste bei jedem gültigen Überschreiten das Event.
        """
        n = 1
        self.logger.debug("adding to bait-o-meter")
        if n <= 0:
            raise ValueError("n must be > 0")
        with self._lock:
            self.value += n
            perc = (self.value/self.max_value) * 100
            self.logger.debug(f"BAITOMETER PERC: {perc}")
            if perc > 0:
                post_event("wledo_meter", perc)


            if self.max_value is not None and self.value > self.max_value:
                self.value = self.max_value

            now = time.monotonic()
            # Rising Edge + Cooldown-Check
            is_rising = self.value >= self.threshold
            
            cooldown_ok = (now - self.last_trigger_ts) >= self.trigger_cooldown
            self.logger.debug(f"cooldown_ok: {cooldown_ok}, rising: {is_rising}")
            if is_rising:
                # starte den Decay, wenn noch nicht geschehen
                self.start_decay()

                if cooldown_ok:
                    self.last_trigger_ts = now
                    event_data = {
                        "value": self.value,
                        "timestamp": now
                    }
                    post_event("threshold_reached", event_data)
                    if not self.isfirst:
                        self.value = self.max_value
                        self.logger.debug("sart streaming now.", event_data)
                        self.isfirst=True
            return self.value

    def _decay_step(self):
        """Ein einzelner Decay-Schritt, wird vom Timer aufgerufen."""
        with self._lock:
            self.value = max(0, self.value - self.decay_amount)
            post_event("wledo_meter", int(96*self.value)/self.max_value)
        self.logger.debug(f"_decay_step {self.max_value},{self.value}")
        # nur weiter planen, wenn nicht gestoppt
        self._schedule_decay()

    def _schedule_decay(self):
        if not self._stop_event.is_set():
            self._timer = threading.Timer(self.decay_interval, self._decay_step)
            self._timer.daemon = True
            self._timer.start()
        if self.value==0:
            post_event("bait o mate says end stream now!", "")
            #self.stop_decay()

# Demo / CLI
if __name__ == "__main__":
    acc = ThresholdAccumulatorSync(
        threshold=5,
        decay_amount=1,
        decay_interval_seconds=10,
        trigger_cooldown_seconds=5
    )

    # KEIN acc.start(); Decay startet automatisch bei erster Überschreitung
    try:
        while True:
            new = acc.add(1)
            acc.logger.debug(f"[{time.strftime('%X')}] added 1 -> {new}")
            time.sleep(3)
    except KeyboardInterrupt:
        acc.logger.debug("Beende...")
        acc.stop_decay()
