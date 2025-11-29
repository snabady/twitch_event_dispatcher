from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event():
    event_name: str
    event_created: datetime.now()
    event_type: IrcEvent | TwitchEvent | BaitEvent    

@dataclass
class IRC_event(Event):
    event_type: str

@dataclass
class TwitchEvent(Event):
    timestamp_created: datetime
    event_source: str
    event_id: str
    event_type: str
    event_data: dict # subclass?

@dataclass
class BaitEvent(Event):
    user: str
    user_id: int


    
