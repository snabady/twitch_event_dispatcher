

def handle_hypetrain_begin(event: dict):
    """
{'id': '5abc2327-b32a-4876-fc23-6f7dcc554dac',
 'broadcaster_user_id': '42226127', 
 'broadcaster_user_login': 'testBroadcaster',
  'broadcaster_user_name': 'testBroadcaster', 
  'total': 879, 
  'progress': 879, 
  'goal': 47180, 
  'top_contributions': [{'user_id': '57680250', 
                        'user_login': 'cli_user1', 
                        'user_name': 'cli_user1', 
                        'type': 'subscription',
                        'total': 548}, 
                        {'user_id': '76863662', 'user_login': 'cli_user2', 'user_name': 'cli_user2', 'type': 'subscription', 'total': 804}
                        ], 
    'last_contribution': {'user_id': '76863662', 'user_login': 'cli_user2', 'user_name': 'cli_user2', 'type': 'subscription', 'total': 804}, 
    'level': 4, 
    'started_at': '2025-06-12T09:04:55.331680+00:00', 
    'expires_at': '2025-06-12T09:09:55.331680+00:00'}  
"""



    event_id = event_data.get("id")
    broadcaster_user_login = event_data.get("broadcaster_user_login")
    broadcaster_user_id = event_data.get("broadcaster_user_id")
    broadcaster_user_name = event_data.get("broadcaster_user_name")
    total = event_data.get("total")
    progress = event_data.get("progress")
    

    """ like begin +++
        cooldown_ends_at """

    print(f"EVENT_DATA: {event_data}")



def handle_hypetrain_end(event: dict):
    event_data = event.get("event_data")
    print(f"EVENT_DATA: {event_data}")
    raise NotImplementedError
def handle_hypetrain_end(event: dict):
    event_data = event.get("event_data")
    print(f"EVENT_DATA: {event_data}")
    raise NotImplementedError
