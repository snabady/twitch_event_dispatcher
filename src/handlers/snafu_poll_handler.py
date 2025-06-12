def handle_poll_begin(event: dict):
    
    """
    {
    'id': '321861e0-b9bf-cebb-12ba-e7ae6557122c', 
    'broadcaster_user_id': '42226127', 
    'broadcaster_user_login': 'testBroadcaster', 
    'broadcaster_user_name': 'testBroadcaster', 
    'title': 'Pineapple on pizza?', 
    'choices': [{'id': '40bc42ff-254b-dfcf-25f5-12595252ead3', 
                'title': 'Yes but choice 1'}, 
                {'id': '26fabdf0-cb21-9845-1079-6687e69904a4', 
                'title': 'Yes but choice 2'}, 
                {'id': '05800fb0-08d7-15d3-4c9d-95fca73a5427', 
                'title': 'Yes but choice 3'}, 
                {'id': '8fe51720-40bc-ff23-2ccc-4c18f91d05fe', 
                'title': 'Yes but choice 4'}], 
    'bits_voting': {'is_enabled': True, 
                    'amount_per_vote': 10}, 
    'channel_points_voting': {'is_enabled': True, 
                              'amount_per_vote': 500}, 
    'started_at': '2025-06-12T06:57:08.531590+00:00', 
    'ends_at': '2025-06-12T07:12:08.531590+00:00'}

    """
    event_data = event.get()
    print(f'EVENT_DATA: {event_data}')
    event_id = event_data.get("id")
    raise NotImplementedError
def handle_poll_end(event: dict):
    print(f'EVENT_DATA: {event_data}')
    event_id = event_data.get("id")
    raise NotImplementedError

def handle_poll_progress(event: dict):
    print(f'EVENT_DATA: {event_data}')
    event_id = event_data.get("id")
    raise NotImplementedError
    raise NotImplementedError