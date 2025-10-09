#!/usr/bin/env python3
import asyncio
from dbus_next.aio import MessageBus
from dbus_next.constants import BusType, MessageType
from dbus_next import Message
import subprocess

AUDACIOUS_SERVICE = "org.atheme.audacious"
AUDACIOUS_PATH = "/org/atheme/audacious"
AUDACIOUS_IFACE = "org.atheme.audacious"

async def get_current_song(bus):
    """Verwendet audtool über D-Bus, um den aktuellen Songtitel zu erhalten."""
    msg = Message(
        destination=AUDACIOUS_SERVICE,
        path=AUDACIOUS_PATH,
        interface=AUDACIOUS_IFACE,
        member="current_song",
    )
    reply = await bus.call(msg)
    if reply.message_type == MessageType.ERROR:
        raise RuntimeError(f"D-Bus-Fehler: {reply.body}")
    return reply.body[0] if reply.body else "(unbekannt)"

async def main():
    bus = await MessageBus(bus_type=BusType.SESSION).connect()

    async def print_song():
        try:
            title = await get_current_song(bus)
            print(f"🎵 Neuer Song: {title}")
        except Exception as e:
            print("Fehler beim Lesen des Songs:", e)

    await print_song()

    def message_handler(message):
        if (
            message.message_type == MessageType.SIGNAL
            and message.interface == AUDACIOUS_IFACE
            and message.member == "current_song_changed"
        ):
            asyncio.create_task(print_song())

    bus.add_message_handler(message_handler)

    print("▶️ Lausche auf Songwechsel ... (Strg+C zum Beenden)")
    await asyncio.get_event_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())

