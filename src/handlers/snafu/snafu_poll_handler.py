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
    event_data = event.get("event_data")
    logger.debug(f'EVENT_DATA: {event_data}')
    event_id                = event_data.get("id")
    broadcaster_user_login  = event_data.get("broadcaster_user_login")
    broadcaster_user_id     = event_data.get("broadcaster_user_id")
    broadcaster_user_name   = event_data.get("broadcaster_user_name")
    title                   = event_data.get("title")
    choices                 = event_data.get("choices")
    bits_voting             = event_data.get("bits_voting")
    channel_points_voting   = event_data.get("channel_points_voting")
    started_at              = event_data.get("started_at")
    ends_at                 = event_data.get("ends_at")
    
    logger.debug("WE DID IT")


def handle_poll_end(event: dict):
    """
    {'id': '32eef3a7-8b58-5b22-8b16-9ea37ab3ca6e', 
    'broadcaster_user_id': '42226127', 
    'broadcaster_user_login': 'testBroadcaster', 
    'broadcaster_user_name': 'testBroadcaster', 
    'title': 'Pineapple on pizza?', 
    'choices': [{'id': 'f667d172-5604-f1b9-d9c5-cff0d4f497a0', '
                title': 'Yes but choice 1', 
                'bits_votes': 5, 
                'channel_points_votes': 3, 
                'votes': 16}, 
                {'id': '3395e6fc-182d-34c6-8741-3edcc31f3f17', 
                'title': 'Yes but choice 2', 
                'bits_votes': 0, 
                'channel_points_votes': 3, 
                'votes': 3}, 
                {'id': 'c84e90b3-f9cf-9873-7db5-284fdbc23f83', 
                'title': 'Yes but choice 3', 
                'bits_votes': 1, 
                'channel_points_votes': 0, 
                'votes': 8}, 
                {'id': '5c8cb7a9-e82e-64b9-d4f1-7026a9e685cb', 
                'title': 'Yes but choice 4',
                'bits_votes': 4, 
                'channel_points_votes': 4, 
                'votes': 8}], 
                'bits_voting': {'is_enabled': True, 'amount_per_vote': 10},
    'channel_points_voting': {'is_enabled': True, 'amount_per_vote': 500}, 
    'status': 'completed', 
    'started_at': '2025-06-12T08:33:31.664116+00:00', 
    'ended_at': '2025-06-12T08:48:31.664116+00:00'}
"""
    event_data = event.get("event_data")
    logger.debug(f'EVENT_DATA: {event_data}')
    event_id                = event_data.get("id")
    broadcaster_user_login  = event_data.get("broadcaster_user_login")
    broadcaster_user_id     = event_data.get("broadcaster_user_id")
    broadcaster_user_name   = event_data.get("broadcaster_user_name")
    title                   = event_data.get("title")
    choices                 = event_data.get("choices")
    bits_voting             = event_data.get("bits_voting")
    channel_points_voting   = event_data.get("channel_points_voting")
    started_at              = event_data.get("started_at")
    ends_at                 = event_data.get("ends_at")
    status                  = event_data.get("status")
    
    
    

def handle_poll_progress(event: dict):
    """
     {'id': '30a92c1e-2bae-b45d-0d1c-ec9b85a4421b', 
     'broadcaster_user_id': '42226127', 
     'broadcaster_user_login': 'testBroadcaster', 
     'broadcaster_user_name': 'testBroadcaster', 
     'title': 'Pineapple on pizza?', 
     'choices': [{'id': '420f0b3b-f96e-5b30-2974-47b3b85a1227', 
                'title': 'Yes but choice 1',
                'bits_votes': 6, 
                'channel_points_votes': 6, 
                'votes': 14}, 
                {'id': 'e87b3a88-a931-fec5-eac3-fbca7ada03f6', 
                'title': 'Yes but choice 2', 
                bits_votes': 0, 
                'channel_points_votes': 9, 
                'votes': 15}, 
                {'id': '123783d0-f940-8c4b-8d78-eb55d2930034', 
                'title': 'Yes but choice 3', 
                'bits_votes': 4, 
                'channel_points_votes': 0, 
                'votes': 11}, 
                {'id': 'f2d33bc9-d0f8-6630-f0a8-0ae858ee142e', 
                'title': 'Yes but choice 4', 
                'bits_votes': 0, 
                'channel_points_votes': 1, 
                'votes': 8}], 
    'bits_voting': {'is_enabled': True, 'amount_per_vote': 10}, 
    'channel_points_voting': {'is_enabled': True, 'amount_per_vote': 500}, 
    'started_at': '2025-06-12T08:48:54.169711+00:00', 
    'ends_at': '2025-06-12T09:03:54.169711+00:00'}
    """
    event_data = event.get("event_data")
    logger.debug(f'EVENT_DATA: {event_data}')
    event_id                = event_data.get("id")
    broadcaster_user_login  = event_data.get("broadcaster_user_login")
    broadcaster_user_id     = event_data.get("broadcaster_user_id")
    broadcaster_user_name   = event_data.get("broadcaster_user_name")
    title                   = event_data.get("title")
    choices                 = event_data.get("choices")
    bits_voting             = event_data.get("bits_voting")
    channel_points_voting   = event_data.get("channel_points_voting")
    started_at              = event_data.get("started_at")
    ends_at                 = event_data.get("ends_at")
    
