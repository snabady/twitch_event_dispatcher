from handlers.twitchapi import myTwitch

class ChannelPointManager:

    def __init__(self, twitch_api: myTwitch):
        self.twitch_api = twitch_api

        
    async def create_custom_reward(self):

        await self.twitch.create_custom_reward(broadcaster_id=self.user.id, 
                                               title="your offline flashkkdfjkdjf", 
                                               background_color="#ffffff",
                                               cost=1001, 
                                               is_enabled=True,
                                               prompt="why?", 
                                               is_user_input_required=False,
                                               #is_max_per_user_per_stream_enabled=True,
                                               #max_per_user_per_stream=1,
                                               is_global_cooldown_enabled=False, 
                                               should_redemptions_skip_request_queue=True)


    async def update_custom_reward():
        raise NotImplementedError


    async def delete_custom_reward():
        raise NotImplementedError

    async def get_custom_reward_redemption():
        raise NotImplementedError
