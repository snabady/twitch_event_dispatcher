def handle_goal_begin(event: dict):

    """
 {'id': '99ae2dd5-9904-a12d-5231-b223a1368d90', 
 'broadcaster_user_id': '42226127',
  'broadcaster_user_name': 'testBroadcaster',
   'broadcaster_user_login': 'testBroadcaster',
    'type': 'follower',
     'description': '',
     'current_amount': 42,
      'target_amount': 184,
       'started_at': '2025-06-12T06:28:14.783962+00:00' 
       }
    
    """
    
    event_data = event.get("event_data")
    print(f'EVENT_DATA: {event_data}')

    description = event_data.get("description")
    current_amount = event_data.get("current_amount")
    target_amount = event_data.get("target_amount")
    started_at = event_data.get("started_at")

    
def handle_goal_end(event: dict):
    """
    {'id': 'b3eca182-dbf3-6125-07e7-acbdd014d66f', 
    'broadcaster_user_id': '42226127', 
    'broadcaster_user_name': 'testBroadcaster', 
    'broadcaster_user_login': 'testBroadcaster', 
    'type': 'follower', 
    'description': '', 
    'is_achieved': False, 
    'current_amount': 27, 
    'target_amount': 899, 
    'started_at': '2025-06-12T06:33:19.666436+00:00', 
    'ended_at': '2025-06-13T06:33:19+00:00'}
"""
    event_data = event.get("event_data")
    print(f'EVENT_DATA: {event_data}')

    event_id = event_data.get("id")
    broadcaster_user_id = event_data.get("broadcaster_user_id")
    broadcaster_user_name = event_data.get("broadcaster_user_name")
    broadcaster_login = event_data.get("broadcaster_user_login")
    event_type = event_data.get("type")
    description = event_data.get("description")
    is_achieved = event_data.get("is_achieved")
    current_amount = event_data.get("current_amount")
    target_amount = event_data.get("target_amount")
    started_at = event_data.get("started_at")
    ended_at = event_data.get("ended_at")
    print("WE_DID_IT")

def handle_goal_progress(event: dict):
    """
    {'id': 'b894cccf-2da4-b037-2140-1fd87773db08', 
    'broadcaster_user_id': '42226127', 
    'broadcaster_user_name': 'testBroadcaster', 
    'broadcaster_user_login': 'testBroadcaster', 
    'type': 'follower', 
    'description': '', 
    'current_amount': 5, 
    'target_amount': 14, 
    'started_at': '2025-06-12T06:37:42.612681+00:00'}
    """
    event_data = event.get("event_data")
    print(f'EVENT_DATA: {event_data}')

    event_id = event_data.get("id")
    broadcaster_user_id = event_data.get("broadcaster_user_id")
    broadcaster_user_login = event_data.get("broadcaster_user_login")
    broadcaster_user_name = event_data.get("broadcaster_user_name")
    event_type = event_data.get("type")
    description = event_data.get("description")
    current_amount = event_data.get("current_amount")
    target_amount = event_data.get("target_amount")
    started_at = event_data.get("started_at")
    