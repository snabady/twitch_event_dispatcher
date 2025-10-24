from twitchAPI.twitch import Twitch, TwitchUser
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import ChannelSubscribeEvent, ChannelRaidEvent, ChannelFollowEvent, StreamOnlineEvent, StreamOfflineEvent, ChannelUpdateEvent, GoalEvent, ChannelPredictionEvent, ChannelPointsCustomRewardRedemptionUpdateEvent, ChannelPointsCustomRewardRedemptionAddEvent, ChannelPointsCustomRewardUpdateEvent, ChannelPointsCustomRewardRemoveEvent, ChannelPointsCustomRewardAddEvent, HypeTrainEvent, HypeTrainEndEvent, ChannelUnbanRequestResolveEvent, ChannelBanEvent, ChannelUnbanEvent, ChannelUnbanRequestCreateEvent, CharityCampaignProgressEvent, CharityCampaignStartEvent, CharityCampaignStopEvent, CharityDonationEvent, ChannelSubscriptionEndEvent, ChannelSubscriptionGiftEvent, ChannelSubscriptionMessageEvent, ChannelShoutoutCreateEvent, ChannelShoutoutReceiveEvent, ChannelCheerEvent,ChannelPointsAutomaticRewardRedemptionAddEvent, ChannelPollBeginEvent, ChannelPollEndEvent, ChannelPollProgressEvent, ChannelModeratorAddEvent, ChannelModeratorRemoveEvent, ChannelBanEvent, ChannelUnbanEvent, ChannelAdBreakBeginEvent
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from twitchAPI.type import TwitchBackendException
from typing import Tuple, Optional
import os
from typing import Union, cast
from utils import log
from dispatcher.event_dispatcher import post_event
from events.twitch_auth_scopes import TARGET_SCOPES, CLI_SCOPES
import logging #.config
import colorlog
import datetime
from utils.log import add_logger_handler
from handlers.db_handler import get_active_channelpoint_rewards

class TwitchEvents:
    """
    Connects to Twitch-Event-Sub via websockets
    use .env for credentials and other settings

    (c) ChaosQueen 5n4fu
    """
    twitch: Optional[Twitch]                = None
    eventsub: Optional[EventSubWebsocket]   = None
    user: Optional[TwitchUser]              = None

    def __init__(self, use_cli: bool):
        self.use_cli_conn = use_cli
        if not use_cli:
            self.logger = logging.getLogger("TWITCH EVENT_SUB")
        else:
            self.logger = logging.getLogger("TWITCH CLI")
        self.log = add_logger_handler(self.logger)
        self.logger.setLevel(logging.DEBUG)      
        self.logger.debug(f"use_cli: {use_cli}")
        self.use_cli_conn = use_cli
        self.event_mapping = self.get_eventmap()

        self.live_auth_scope = TARGET_SCOPES
        self.cli_auth_scopes = CLI_SCOPES
        
        self.event_map = self.get_eventmap()

        self.channelpoint_rewards = self.init_active_channelpoint_rewards()
        self.live_auth_scope = TARGET_SCOPES
        self.cli_auth_scopes = CLI_SCOPES
        self.twitch_cli_commands = []
        self.setEnv()
        

    def init_active_channelpoint_rewards(self):
        self.channelpoint_reward =  get_active_channelpoint_rewards()

    async def __aenter__(self):
        
        if self.use_cli_conn:
            self.logger.debug("__aenter__ cli - setting up eventsub")
            self.eventsub, self.twitch, self.user = await self.climockingConn()
        else:
            self.logger.debug("__aenter__ live - setting up eventsub")
            self.eventsub, self.twitch, self.user = await self.prodConn()
        self.eventsub.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        
        await self.eventsub.stop()
        await self.twitch.close()
        self.logger.debug("aexit")
        return self

    def setEnv(self):
        """
        loads the .env variables
        adjust variables in .env File 
        """
        if self.use_cli_conn:
            self.TWITCH_CLI_MOCK_API_URL    = os.getenv("TWITCH_CLI_MOCK_API_URL", "BASE_URL not found") 
            self.AUTH_BASE_URL              = os.getenv("AUTH_BASE_URL", "BASE_URL not found")
            self.TWITCH_CLI_CONNECTION_URL  = os.getenv("TWITCH_CLI_CONNECTION_URL", "BASE_URL not found")
            self.TWITCH_SUBSCRIPTION_URL    = os.getenv("TWITCH_SUBSCRIPTION_URL", "SUBSCRIPTION_URL")
            self.CLI_CLIENT_SECRET          = os.getenv("CLI_CLIENT_SECRET", "CLI_S not found")
            self.CLI_USER_ID                = os.getenv("CLI_USER_ID", "CLI_UID not found")
            self.CLI_CLIENTID               = os.getenv("CLI_CLIENTID", "CLI_ID not found")
            
        else:
            self.CLIENT_ID          = os.getenv("LIVE_CLIENT_ID", "LIVE_CLIENT_ID not found")
            self.CLIENT_S           = os.getenv("LIVE_CLIENT_SECRET", "LIVE_CLIENT_SECRET not found")

       
    async def prodConn(self) -> Tuple[EventSubWebsocket, Twitch, TwitchUser]:
        """
        creates a connection to Twitch EventSub using websockets
        u need a app registered at twitch -> .env
                twitch = await Twitch(self.CLIENT_ID, self.CLIENT_S,)
        helper = UserAuthenticationStorageHelper(twitch, auth_scope.TARGET_SCOPES)
        await helper.bind()
        user = await first(twitch.get_users())

        eventsub = EventSubWebsocket(twitch)
        
        return eventsub, twitch, user
        """
        #self.logger.debug(f"c_id: {self.CLIENT_ID} s. {self.CLIENT_S}")
        twitch = await Twitch(self.CLIENT_ID, self.CLIENT_S,)
        helper = UserAuthenticationStorageHelper(twitch, self.live_auth_scope)
        await helper.bind()
        user = await first(twitch.get_users())
        eventsub = EventSubWebsocket(twitch)
        return eventsub, twitch, user

    async def climockingConn(self) -> Tuple[EventSubWebsocket, Twitch, TwitchUser]:
        """
        connect to mock-cli WS -> trigger commands per twitch cmdl
        connect to eventsocked
        and get the TwitchUser using this connection
        https://dev.twitch.tv/docs/cli/event-command/ event commands for twitch-cli
        credentials and server settings in .env

        TODO AuthScopes compare || check if normal working
        """
        twitch = await Twitch(self.CLI_CLIENTID,
                            self.CLI_CLIENT_SECRET,
                            base_url        = self.TWITCH_CLI_MOCK_API_URL, 
                            auth_base_url   = self.AUTH_BASE_URL)
        self.logger.debug(f"twitch: {type(twitch)}")
        twitch.auto_refresh_auth = False # cli needs no refreshing
        auth = UserAuthenticator(twitch, 
                                 self.cli_auth_scopes, 
                                 auth_base_url=self.AUTH_BASE_URL)
        #x = self.CLI_UID

        token = await auth.mock_authenticate(self.CLI_USER_ID)
        await twitch.set_user_authentication(token,
                                             self.cli_auth_scopes)
        #self.logger.debug(f"scopes: {self.cli_auth_scopes}" )
        user = await first(twitch.get_users())
        self.logger.debug(f"auth: {user}")
        eventsub = EventSubWebsocket(twitch,
                                    connection_url=self.TWITCH_CLI_CONNECTION_URL,
                                    subscription_url=self.TWITCH_SUBSCRIPTION_URL)
        return eventsub, twitch, user
    

    
    def get_eventmap(self):
        return     { 
        ChannelSubscribeEvent: "twitch_subscribe_event",
        ChannelSubscriptionEndEvent:"twitch_subscribe_event",
        ChannelSubscriptionGiftEvent:"twitch_subscribe_event",
        ChannelSubscriptionMessageEvent:"twitch_subscribe_event",
        ChannelRaidEvent:"twitch_action_event",
        ChannelFollowEvent:"twitch_action_event",
        ChannelCheerEvent:"twitch_action_event",
        StreamOnlineEvent:"twitch_streaminfo_event",
        StreamOfflineEvent:"twitch_streaminfo_event",
        ChannelUpdateEvent:"twitch_streaminfo_event",
        GoalEvent:"twitch_goal_event",
        ChannelPredictionEvent:"",
        ChannelPointsCustomRewardRedemptionUpdateEvent:"twitch_channelpoint_event",
        ChannelPointsCustomRewardRedemptionAddEvent:"twitch_channelpoint_event",
        ChannelPointsCustomRewardUpdateEvent:"twitch_channelpoint_event",
        ChannelPointsCustomRewardRemoveEvent:"twitch_channelpoint_event",
        ChannelPointsCustomRewardAddEvent:"twitch_channelpoint_event",
        ChannelPointsAutomaticRewardRedemptionAddEvent:"twitch_channelpoint_event",
        HypeTrainEvent:"twitch_hypetrain_event",
        HypeTrainEndEvent:"twitch_hypetrain_event",
        ChannelUnbanRequestResolveEvent:"twitch_ban_event",
        ChannelBanEvent:"twitch_ban_event",
        ChannelUnbanEvent:"twitch_ban_event",
        ChannelUnbanRequestCreateEvent:"twitch_ban_event",
        CharityCampaignProgressEvent:"twitch_charity_event",
        CharityCampaignStartEvent:"twitch_charity_event",
        CharityCampaignStopEvent:"twitch_charity_event",
        CharityDonationEvent:"twitch_charity_event",
        ChannelShoutoutCreateEvent:"twitch_shoutout_event",
        ChannelShoutoutReceiveEvent:"twitch_shoutout_event",
        ChannelPollBeginEvent: "twitch_poll_event",
        ChannelPollEndEvent: "twitch_poll_event",
        ChannelPollProgressEvent: "twitch_poll_event"
        } 
    
    async def dispatch_twitch_event(self, x: Union[ChannelSubscribeEvent, ChannelBanEvent, ChannelFollowEvent, ChannelRaidEvent, ChannelCheerEvent]):
        event_source = "twitch_event"
        ts = datetime.datetime.now()
        data = ""
        self.logger.debug(f'x: {type(x)}')
        if self.event_map[type(x)] != None:
            
            x = cast(ChannelSubscribeEvent, x)

            self.logger.debug(f"dispatching **** event_type:------> >>> {x.subscription.type} <<<")
            
            data = {
                "timestamp_received": ts, 
                "timestamp_created": x.subscription.created_at,
                "event_source": event_source,
                "event_id": x.subscription.id,
                "event_type": x.subscription.type,
                "type": self.event_map[type(x)],
                "event_data": x.event.to_dict()
            }
            self.logger.debug(f"**POST TWITCH EVENT**: {self.event_map[type(x)]} ")
            post_event(self.event_map[type(x)], data)
    

         
    async def listen_stream_info_events(self):
        """
        EVENT_LISTENER

        subscribes to stream Info related Events - exactly to: 

            listen_stream_online
            listen_stream_offline
            listen_channel_update_v2
            listen_channel_update

        For more information see here: 
        https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#streamonline
        https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#streamoffline
        https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelupdate
        https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelupdate

        """
        streamonline_id     = await self.eventsub.listen_stream_online(self.user.id, self.dispatch_twitch_event)  
        streamoffline_id    = await self.eventsub.listen_stream_offline(self.user.id, self.dispatch_twitch_event)   
        channelupdatev2_id  = await self.eventsub.listen_channel_update_v2(self.user.id, self.dispatch_twitch_event)
        channelupdate_id    = await self.eventsub.listen_channel_update(self.user.id,self.dispatch_twitch_event)
        self.logger.info("successfully subscribed to stream_info_events")
        return {
            "stream.online": streamonline_id,
            "stream.offline": streamoffline_id,
            "channel.update_v2": channelupdatev2_id,
            "channel.update": channelupdate_id
        }

    async def listen_channel_goal_events(self):
        """
        channel.goal.begin
        channel.goal.end 
        channel.goal.progress
        """

        goal_begin_id       = await self.eventsub.listen_goal_begin(self.user.id, self.dispatch_twitch_event)
        goal_end_id         = await self.eventsub.listen_goal_end(self.user.id, self.dispatch_twitch_event)
        goal_progress_id    = await self.eventsub.listen_goal_progress(self.user.id, self.dispatch_twitch_event)

        self.logger.info("successfully subscribed to channel_goal_events")
        return {

        "channel.goal.begin": goal_begin_id,
        "channel.goal.end" : goal_end_id,
        "channel.goal.progress": goal_progress_id

        }

    async def listen_channel_polls(self):
        """
        channel.poll.begin 
        channel.poll.end
        channel.poll.progress   
        """
        poll_begin_id       = await self.eventsub.listen_channel_poll_begin(self.user.id, self.dispatch_twitch_event) 
        poll_end_id         = await self.eventsub.listen_channel_poll_end(self.user.id, self.dispatch_twitch_event)
        poll_progress_id    = await self.eventsub.listen_channel_poll_progress(self.user.id, self.dispatch_twitch_event)

        self.logger.info("successfully subscribed to channel_poll_events")
        return {
            "channel.poll.begin" : poll_begin_id, 
            "channel.poll.end": poll_end_id,
            "channel.poll.progress"   : poll_progress_id
        }

    async def listen_channel_predictions(self):
        """
        channel.prediction.begin
        channel.prediction.end
        channel.prediction.lock
        channel.prediction.progress
        """

        prediction_begin_id         = await self.eventsub.listen_channel_prediction_begin(self.user.id, self.dispatch_twitch_event)
        prediction_end_id           = await self.eventsub.listen_channel_prediction_end(self.user.id, self.dispatch_twitch_event)
        prediction_lock_id          = await self.eventsub.listen_channel_prediction_lock(self.user.id, self.dispatch_twitch_event)
        prediction_progress_id      = await self.eventsub.listen_channel_prediction_progress(self.user.id, self.dispatch_twitch_event)

        self.logger.info("successfully subscribed to channel_prediction_events")
        return {
            "channel.prediction.begin": prediction_begin_id, 
            "channel.prediction.end": prediction_end_id,
            "channel.prediction.lock": prediction_lock_id,
            "channel.prediction.progress": prediction_progress_id
        }



    async def listen_channel_points(self):
        """

        # TODO: auto_reward_redemption
        channel.channel_points_custom_reward.add 
        channel.channel_points_custom_reward.remove 
        channel.channel_points_custom_reward.update 
        channel.channel_points_custom_reward_redemption.add
        channel.channel_points_custom_reward_redemption.update
        """
        try:
            reward_add_id                       = await self.eventsub.listen_channel_points_custom_reward_add(self.user.id, self.dispatch_twitch_event)
            reward_remove_id                    = await self.eventsub.listen_channel_points_custom_reward_remove(self.user.id, self.dispatch_twitch_event)
            reward_update_id                    = await self.eventsub.listen_channel_points_custom_reward_update(self.user.id, self.dispatch_twitch_event)
            redemption_add_id                   = await self.eventsub.listen_channel_points_custom_reward_redemption_add(self.user.id, self.dispatch_twitch_event)
            redemption_update_id                = await self.eventsub.listen_channel_points_custom_reward_redemption_update(self.user.id, self.dispatch_twitch_event)
            automatic_reward_redemption_add_id  = await self.eventsub.listen_channel_points_automatic_reward_redemption_add(self.user.id, self.dispatch_twitch_event)
            #auto_reward_redemption = await self.eventsub.listen_channel_points_automatic_reward_redemption_add(self.user.id, self.on_twitch_event)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
        

        return {
            "channel.channel_points_custom_reward.add" : reward_add_id,
            "channel.channel_points_custom_reward.remove" : reward_remove_id,
            "channel.channel_points_custom_reward.update" : reward_update_id,
            "channel.channel_points_custom_reward_redemption.add": redemption_add_id,
            "channel.channel_points_custom_reward_redemption.update": redemption_update_id,
            "channel.channel_points_automatic_reward_redemption.add": automatic_reward_redemption_add_id
        }


        self.logger.info("successfully subscribed to channel_point_events")


    async def listen_hype_train(self):
        """
        channel.hype_train.begin 
        channel.hype_train.end 
        channel.hype_train.progress
        """

        hype_train_begin_id    = await self.eventsub.listen_hype_train_begin(self.user.id, self.dispatch_twitch_event)
        hype_train_end_id      = await self.eventsub.listen_hype_train_end(self.user.id, self.dispatch_twitch_event)
        hype_train_progress_id = await self.eventsub.listen_hype_train_progress(self.user.id, self.dispatch_twitch_event)

        self.logger.info("successfully subscribed to hype_train_events")

        return {
            "channel.hype_train.begin" : hype_train_begin_id,
            "channel.hype_train.end" : hype_train_end_id,
            "channel.hype_train.progress" : hype_train_progress_id
        }

    async def listen_ban_events(self):
        """
        ATTENTION: PROBABLY NOT WORKING WITHIN CLI!


        channel.ban 
        channel.unban
        channel.unban_request.create
        channel.unban_request.resolve
        TODO: mod? ->


        """
        ban_id                = await self.eventsub.listen_channel_ban(self.user.id, self.dispatch_twitch_event)
        unban_id              = await self.eventsub.listen_channel_unban(self.user.id, self.dispatch_twitch_event)
        unban_request_id      = await self.eventsub.listen_channel_unban_request_create(self.user.id, self.user.id, self.dispatch_twitch_event)
        unban_request_resolve_id = await self.eventsub.listen_channel_unban_request_resolve(self.user.id, self.user.id, self.dispatch_twitch_event)

        self.logger.info("successfully subscribed to ban_events")

        return {
            "channel.ban": ban_id,
            "channel.unban": unban_id,
            "channel.unban_request.create": unban_request_id,
            "channel.unban_request.create": unban_request_resolve_id
        }

    async def listen_charity_events(self):
        """
        channel.charity_campaign.donate 
        channel.charity_campaign.progress
        channel.charity_campaign.start 
        channel.charity_campaign.stop
        """
        charity_donate_id   = await self.eventsub.listen_channel_charity_campaign_donate(self.user.id, self.dispatch_twitch_event)
        charity_progress_id = await self.eventsub.listen_channel_charity_campaign_progress(self.user.id, self.dispatch_twitch_event)
        charity_start_id    = await self.eventsub.listen_channel_charity_campaign_start(self.user.id, self.dispatch_twitch_event)
        charity_stop_id     = await self.eventsub.listen_channel_charity_campaign_stop(self.user.id, self.dispatch_twitch_event)

        self.logger.info("successfully subscribed to charity_events")
        return {
            "channel.charity_campaign.donate" : charity_donate_id,
            "channel.charity_campaign.progress": charity_progress_id,
            "channel.charity_campaign.start" : charity_start_id,
            "channel.charity_campaign.stop": charity_stop_id
        }

    async def listen_shoutout_events(self):
        """
        channel.shoutout.create
        channel.shoutout.receive
        """
        shoutout_create_id  = await self.eventsub.listen_channel_shoutout_create(self.user.id, self.user.id, self.dispatch_twitch_event)
        shoutout_receive_id = await self.eventsub.listen_channel_shoutout_receive(self.user.id, self.user.id,  self.dispatch_twitch_event)

        self.logger.info("successfully subscribed to shoutout_events")

        return {
            "channel.shoutout.create": shoutout_create_id,
            "channel.shoutout.receive": shoutout_receive_id
        }

    async def listen_subscribe_events(self) :
        """
        twitch-cli-endpoint-names:
        channel.subscribe
        channel.subscription.end
        channel.subscription.gift
        channel.subscription.message
        """
        subscribe_id            = await self.eventsub.listen_channel_subscribe(self.user.id, self.dispatch_twitch_event)
        subscription_end_id     = await self.eventsub.listen_channel_subscription_end(self.user.id, self.dispatch_twitch_event)
        subscription_gift_id    = await self.eventsub.listen_channel_subscription_gift(self.user.id, self.dispatch_twitch_event)
        subscription_message_id = await self.eventsub.listen_channel_subscription_message(self.user.id, self.dispatch_twitch_event)
        
        self.logger.info("subscribed to subscribe_events")
        
        # -> cli-command name as key, for automation
        return  {
            "channel.subscribe":subscribe_id,
            "channel.subscription.end":subscription_end_id,
            "channel.subscription.gift": subscription_gift_id,
            "channel.subscription.message": subscription_message_id
        }

    async def listen_moderate_events(self):
        """
        channel.moderator.add 
        channel.moderator.remove
        channel.ad_break.begin 
        """
        mod_add_id          = await self.eventsub.listen_channel_moderator_add(self.user.id, self.dispatch_twitch_event)
        mod_remove_id       = await self.eventsub.listen_channel_moderator_remove(self.user.id, self.dispatch_twitch_event)
        ad_break_begin_id   = await self.eventsub.listen_channel_ad_break_begin(self.user.id, self.dispatch_twitch_event)

        self.logger.info("successfully subscribed to moderate_events")
        return {

            "channel.moderator.add" : mod_add_id,
            "channel.moderator.remove": mod_remove_id,
            "channel.ad_break.begin" : ad_break_begin_id
        }

    async def listen_channel_action_events(self):
        """
        channel.cheer 
        channel.follow 
        channel.raid 
        """
        try:
            #self.logger.debug("channel_action_events")
            raid_id = await self.eventsub.listen_channel_raid(self.dispatch_twitch_event, self.user.id, None)
            #self.logger.debug(f"raid_id {raid_id}")
            follow_id = await self.eventsub.listen_channel_follow_v2(self.user.id, self.user.id, self.dispatch_twitch_event)

            #self.logger.debug(f"follow_id {follow_id}")
            channel_cheer_id = await self.eventsub.listen_channel_cheer(self.user.id, self.dispatch_twitch_event)
            
            #self.logger.debug(f"cheer_id {channel_cheer_id}")
        except Exception as e:
            self.logger.debug(e)
        self.logger.info("successfully subscribed to channel_action_events")
        return {
            "channel.cheer" : channel_cheer_id,
            "channel.follow" : follow_id,
            "channel.raid" : raid_id
        }


    async def collection_of_events_not_supported_with_cli(self):
        """
        ATTENTION: you cant use this fct. when self.use_cli = True! only in production or simulation
        """
        try:
            # The combination of values in the type and version fields is not valid
            sub_message_id = await self.eventsub.listen_channel_points_automatic_reward_redemption_add(self.user.id, self.onPointsAutoRewardRedemptionAdd)

            self.logger.debug(f'twitch event trigger channel.subscription.message -t {self.user.id} -u {self.sub_message_id} -T websocket') 
        except TwitchBackendException as e:
            self.logger.error(f'TwitchBackendException: {e}')
        except Exception as e:
            self.logger.error('collection_of_events' , e)



