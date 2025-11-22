from __future__ import annotations
import logging
import os
import asyncio
import json
import simpleobsws
from src.utils import log
from src.dispatcher.event_dispatcher import post_event, subscribe_event
from simpleobsws import enum as enums
from src.handlers import obs_handler
from typing import Optional, Awaitable, Any

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)



def set_source_visibility_wrapper(scene_name, source_name, visible):

    #    logger.debug(f'scene_name: {scene_name}\tsource_name: {source_name}\tvisible: {visible}')
    async def runner():
        obs = Obsws()
        scene_item_id = await obs.get_scene_item_id(scene_name, source_name)
#        await obs.set_source_visibility(scene_name, scene_item_id, not visible)
#        await asyncio.sleep(0.1)
        await obs.set_source_visibility(scene_name, scene_item_id, visible)

    Obsws().enqueue(runner())


def switch_scene_wrapper(scene_name: str):
    async def runner():
        obs = Obsws()
        await obs.switch_scene(scene_name)

    Obsws().enqueue(runner())


def trigger_hotkey_by_name_wrapper(hotkey_name: str):
    async def runner():
        obs = Obsws()
        await obs.trigger_hotkey_by_name(hotkey_name)

    Obsws().enqueue(runner())


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # cls._instances[cls] = super(Singleton, cls).__call__(*args,**kwargs)
        # return cls._instances[cls]
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Obsws(metaclass=Singleton):
    """
    OBS WebSocket client with connection management:
    - background connection manager that polls/retries every X seconds (configurable via ENV)
    - health checks while connected
    - queue worker that attempts to run queued tasks if connected, otherwise the task is skipped
      (and a notification is emitted) — avoids re-enqueue storms and avoids exceptions flooding logs.
    - safe_call posts an event when a request cannot be delivered.
    """

    def __init__(self):
        self.obs_task_queue = asyncio.Queue()
        self.ws: Optional[simpleobsws.WebSocketClient] = None
        self.logger = logging.getLogger("OBSWS")
        if not self.logger.hasHandlers():
            log.add_logger_handler(self.logger)
        self.logger.setLevel(logging.INFO)

        # connection management primitives
        self._connect_lock = asyncio.Lock()
        self._connected_event = asyncio.Event()
        self._stop = False

        self._reconnect_interval = float(os.getenv("OBSWS_RECONNECT_INTERVAL_SECONDS", "300"))  # default 5 minutes
        # healthcheck interval while connected
        self._healthcheck_interval = float(os.getenv("OBSWS_HEALTHCHECK_INTERVAL", "15"))
        # how long a worker should wait for connection before giving up on that queued task
        self._task_wait_for_conn = float(os.getenv("OBSWS_TASK_WAIT_FOR_CONNECTION_SECONDS", "5"))

        # start workers
        asyncio.create_task(self.obs_task_worker())
        asyncio.create_task(self._connection_manager())

        self.logger.debug("Hello from obsws")
        subscribe_event("obs_set_source_visibility", self.obs_set_source_visibility)
        subscribe_event("obs_scene_change", self.obs_scene_change)
        subscribe_event("obs_set_input_mute", self.obs_set_input_mute)
        self.setEnv()
        self.set_event_map()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()

    def setEnv(self):
        """
        loads the .env variables
        """
        self.obs_url = os.getenv("OBSWS_URL", "ws://127.0.0.1:4455")
        self.password = os.getenv("OBSWS_PASSWORD", None)

    async def stop(self):
        """Gracefully stop background tasks and disconnect."""
        self._stop = True
        try:
            if self.ws:
                await self.ws.disconnect()
        except Exception as e:
            self.logger.debug("Error during stop disconnect: %s", e)
        self.ws = None
        self._connected_event.clear()

    async def obs_task_worker(self):
        """
        Process queued tasks.
        Behaviour changed to match your request:
        - If there's a connection, run the task.
        - If there's no connection within _task_wait_for_conn seconds, the task is skipped (not re-enqueued)
          and a post_event('obs_task_skipped', {...}) is emitted so you can react/log that 'xy' wasn't executed.
        This prevents repeated exceptions when OBS is closed and gives a single notification per skipped task.
        """
        while not self._stop:
            task_coro = await self.obs_task_queue.get()
            try:
                # wait for connection for a short time (configurable). If not connected within this window, skip task.
                try:
                    await asyncio.wait_for(self._connected_event.wait(), timeout=self._task_wait_for_conn)
                except asyncio.TimeoutError:
                    # no connection - SKIP this task and notify
                    coro_repr = repr(task_coro)
                    self.logger.warning("Skipping OBS task (no connection): %s", coro_repr)
                    try:
                        post_event("obs_task_skipped", {"coro": coro_repr, "reason": "no_connection"})
                    except Exception:
                        # ensure post_event issues do not crash the worker
                        self.logger.debug("post_event failed for obs_task_skipped")
                    # important: close coroutine to avoid "coroutine was never awaited" warning
                    if asyncio.iscoroutine(task_coro):
                        try:
                            task_coro.close()
                        except Exception:
                            pass
                    continue

                # connection is set -> run the task
                await task_coro
            except Exception as e:
                # Catch everything here to avoid crashing the worker or flooding logs with repeated exceptions.
                self.logger.exception("OBS_TASK_WORKER error while executing queued task: %s", e)
                try:
                    post_event("obs_task_error", {"error": str(e), "task": repr(task_coro)})
                except Exception:
                    self.logger.debug("post_event failed for obs_task_error")
            finally:
                try:
                    self.obs_task_queue.task_done()
                except Exception:
                    pass
            await asyncio.sleep(0.01)

    def set_event_map(self):
        self.event_map = {
            "MediaInputPlaybackEnded": obs_handler.media_input_playback_ended,
            "SceneItem": obs_handler.blub
        }

    def obs_set_source_visibility(self, event):
        event = event.get("event_data")
        if not event.get("visible"):
            self.enqueue(self.set_source_visibility(event.get("scene_name"), event.get("source_name"), True))
            self.enqueue(self.set_source_visibility(event.get("scene_name"), event.get("source_name"), False))
        else:
            self.enqueue(self.set_source_visibility(event.get("scene_name"), event.get("source_name"), False))
            self.enqueue(self.set_source_visibility(event.get("scene_name"), event.get("source_name"), True))
        self.enqueue(self.set_source_visibility(event.get("scene_name"), event.get("source_name"), event.get("visible")))

    def obs_scene_change(self, event):
        raise NotImplementedError

    def enqueue(self, coro: Awaitable):
        """
        Enqueue a coroutine that will be executed by the worker.
        The worker will only execute it when a connection exists; otherwise the task gets skipped
        and a notification is emitted.
        """
        if not asyncio.iscoroutine(coro):
            raise ValueError("enqueue expects a coroutine")
        self.logger.debug(self)
        self.obs_task_queue.put_nowait(coro)
        self.logger.debug(f"OBS_QUEUE: {self.obs_task_queue.qsize()}")

    async def _connect(self) -> bool:
        """Try to connect once and set connected_event on success."""
        async with self._connect_lock:
            if self.ws is not None:
                # check if already connected and identified
                try:
                    request = simpleobsws.Request("GetVersion")
                    resp = await self.ws.call(request)
                    if resp and resp.ok():
                        self.logger.debug("Already connected and healthy")
                        self._connected_event.set()
                        return True
                except Exception:
                    # fall through to reconnect
                    pass

            # create and connect
            try:
                self.logger.debug("Connecting to OBS WebSocket at %s", self.obs_url)
                self.ws = simpleobsws.WebSocketClient(self.obs_url, password=self.password)
                await self.ws.connect()
                await self.ws.wait_until_identified()
                # register callback
                self.ws.register_event_callback(self.on_event)
                self._connected_event.set()
                self.logger.info("Connected and identified with OBS WebSocket")
                try:
                    post_event("obs_connected", {"url": self.obs_url})
                except Exception:
                    self.logger.debug("post_event failed for obs_connected")
                return True
            except Exception as e:
                self.logger.debug("Failed to connect to OBS: %s", e)
                # cleanup partially created ws
                try:
                    if self.ws:
                        await self.ws.disconnect()
                except Exception:
                    pass
                self.ws = None
                self._connected_event.clear()
                return False

    async def init_obswebsocket_ws(self):
        """Legacy entry point - keep for compatibility."""
        return await self._connect()

    async def _connection_manager(self):
        """
        Background task:
        - If disconnected, try to connect every _reconnect_interval seconds (user requested 'nach x Minuten nochmal schauen').
        - If connected, perform periodic healthchecks every _healthcheck_interval seconds; on failure clear connection.
        """
        while not self._stop:
            if not self._connected_event.is_set() or not self.ws:
                # attempt a connect, but do not spam: retry only once per _reconnect_interval
                ok = await self._connect()
                if not ok:
                    self.logger.debug("Will retry connect after %.1fs", self._reconnect_interval)
                    await asyncio.sleep(self._reconnect_interval)
                    continue
                else:
                    # connected -> loop around to healthcheck
                    continue

            # when connected: perform healthcheck
            try:
                await asyncio.sleep(self._healthcheck_interval)
                request = simpleobsws.Request("GetVersion")
                resp = await self.ws.call(request)
                if not resp or not resp.ok():
                    raise RuntimeError("Healthcheck response not ok")
            except Exception as e:
                self.logger.warning("Connection lost or unhealthy: %s", e)
                try:
                    if self.ws:
                        await self.ws.disconnect()
                except Exception:
                    pass
                self.ws = None
                self._connected_event.clear()
                try:
                    post_event("obs_disconnected", {"reason": str(e)})
                except Exception:
                    self.logger.debug("post_event failed for obs_disconnected")
                # after clearing, the loop will wait _reconnect_interval before next attempt
                await asyncio.sleep(self._reconnect_interval)

    async def get_scene_item_id(self, scene_name, source_name):
        """Return sceneItemId (or None)"""
        self.logger.debug(f"get_scene_item_id {scene_name} .. {source_name}")
        request = simpleobsws.Request("GetSceneItemId", {
            "sceneName": scene_name,
            "sourceName": source_name
        })
        response = await self._safe_call(request)
        if response and response.ok():
            self.logger.debug(f'{scene_name}|{source_name}: got sceneItemId: {response.responseData["sceneItemId"]}')
            return response.responseData["sceneItemId"]
        else:
            self.logger.debug("response not ok, from get_scene_item_id")
            try:
                post_event("obs_call_failed", {"request": "GetSceneItemId", "scene": scene_name, "source": source_name})
            except Exception:
                pass
            return None

    async def set_source_visibility(self, scene_name, scene_item_id, visible=False):
        # if the provided scene_item_id is actually a source name, resolve it
        if isinstance(scene_item_id, str):
            scene_item_id = await self.get_scene_item_id(scene_name, scene_item_id)

        request = simpleobsws.Request("SetSceneItemEnabled", {
            "sceneName": scene_name,
            "sceneItemId": scene_item_id,
            "sceneItemEnabled": visible
        })
        _ = await self._safe_call(request)
        # no return value expected

    async def switch_scene(self, scene_name):
        request = simpleobsws.Request(
            requestType='SetCurrentProgramScene',
            requestData={'sceneName': scene_name})
        _ = await self._safe_call(request)

    def obs_set_input_mute(self, event):
        event_data = event.get("event_data")
        audiosource = event_data.get("audiosource")
        muted = event_data.get("muted")

        self.enqueue(self.set_input_mute(muted, audiosource))

    async def set_input_mute(self, muted: bool, audiosource: str):
        request = simpleobsws.Request(requestType="SetInputMute",
                                      requestData={"inputName": audiosource,
                                                   "inputMuted": muted})
        _ = await self._safe_call(request)

    async def on_event(self, eventType, eventData):
        if eventData is None:
            self.logger.debug(f"eventType: {eventType}")
            return

        if eventData.get("inputName") != "TimerText":
            self.logger.debug(eventData.get("inputName"))
        if not (eventType == "InputSettingsChanged" and eventData.get("inputName") == "TimerText"):
            self.logger.info('event_triggered Type: {} | Raw Data: {}'.format(eventType, eventData))
        if eventType == "MediaInputPlaybackEnded" and eventData.get("inputName") == "raid_audio":
            await self.set_input_mute(False, "desktop_audio")
            await self.set_source_visibility("ALERTS", "raid_overlay", False)

    async def trigger_hotkey_by_name(self, hotkey_name):
        request = simpleobsws.Request("TriggerHotkeyByName", {"hotkeyName": hotkey_name})
        response = await self._safe_call(request)
        self.logger.debug("trigger_hotkey_by_name ok=%s", bool(response and response.ok()))

    async def reload_browser_source(self, browser_source_name: str):
        request = simpleobsws.Request(
            "PressInputPropertiesButton",
            {
                "inputName": browser_source_name,
                "propertyName": "refreshnocache"
            }
        )
        response = await self._safe_call(request)
        self.logger.debug("Reload requested: %s", bool(response and response.ok()))
        # don't disconnect here - keep connection open for reuse

    async def subscribe_events(self):
        event_subs = (
            simpleobsws.enums.EventSubscription.MediaInputs |
            simpleobsws.enums.EventSubscription.SceneItems |
            simpleobsws.enums.EventSubscription.Transitions |
            simpleobsws.enums.EventSubscription.Outputs |
            simpleobsws.enums.EventSubscription.Filters |
            simpleobsws.enums.EventSubscription.General |
            simpleobsws.enums.EventSubscription.Config |
            simpleobsws.enums.EventSubscription.Scenes |
            simpleobsws.enums.EventSubscription.Inputs |
            simpleobsws.enums.EventSubscription.Vendors |
            simpleobsws.enums.EventSubscription.Ui
        )
        request = simpleobsws.Request("SubscribeEvents", {
            "eventSubscriptions": event_subs
        })
        response = await self._safe_call(request)
        self.logger.debug("SubscribeEvents ok=%s", bool(response and response.ok()))

    async def _safe_call(self, request: simpleobsws.Request, retry: bool = True) -> Optional[Any]:
        """
        Ensures connected and performs a call.
        - If there's no connection, returns None (no exception).
        - If call fails, tries one reconnect attempt (subject to reconnect interval) and retries once.
        - On final failure posts an 'obs_call_failed' event with basic info so upper layers can handle/report.
        """
        # If not connected, try a single immediate connect attempt (but don't block forever)
        if not self._connected_event.is_set():
            # attempt connect now (non-spamming: connection manager will continue trying in background)
            await self._connect()

        if not self._connected_event.is_set() or not self.ws:
            # no connection available -> inform and return None
            try:
                # gather some info for the event; Request has attributes but fallback to repr
                req_info = getattr(request, "requestType", None) or getattr(request, "request_type", None) or str(request)
                post_event("obs_call_failed", {"request": req_info, "reason": "no_connection"})
            except Exception:
                self.logger.debug("post_event failed for obs_call_failed (no_connection)")
            self.logger.debug("No active OBS connection; _safe_call returning None for %s", repr(request))
            return None

        try:
            response = await self.ws.call(request)
            return response
        except Exception as e:
            self.logger.debug("Call failed: %s", e)
            # attempt one reconnect + retry
            if retry:
                self.logger.info("Attempting reconnect after call failure")
                await self._connect()
                if not self._connected_event.is_set() or not self.ws:
                    try:
                        post_event("obs_call_failed", {"request": getattr(request, "requestType", str(request)), "reason": "reconnect_failed"})
                    except Exception:
                        pass
                    return None
                try:
                    response = await self.ws.call(request)
                    return response
                except Exception as e2:
                    self.logger.exception("Retry after reconnect failed: %s", e2)
                    try:
                        post_event("obs_call_failed", {"request": getattr(request, "requestType", str(request)), "reason": str(e2)})
                    except Exception:
                        pass
                    return None
            try:
                post_event("obs_call_failed", {"request": getattr(request, "requestType", str(request)), "reason": str(e)})
            except Exception:
                pass
            return None
