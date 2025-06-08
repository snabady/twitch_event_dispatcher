from twitchAPI.twitch import Twitch, TwitchUser
from twitchAPI.oauth import UserAuthenticator, UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import ChannelSubscribeEvent, ChannelRaidEvent, ChannelFollowEvent, StreamOnlineEvent, StreamOfflineEvent, ChannelUpdateEvent, GoalEvent, ChannelPredictionEvent, ChannelPointsCustomRewardRedemptionUpdateEvent, ChannelPointsCustomRewardRedemptionAddEvent, ChannelPointsCustomRewardUpdateEvent, ChannelPointsCustomRewardRemoveEvent, ChannelPointsCustomRewardAddEvent, HypeTrainEvent, HypeTrainEndEvent, ChannelUnbanRequestResolveEvent, ChannelBanEvent, ChannelUnbanEvent, ChannelUnbanRequestCreateEvent, CharityCampaignProgressEvent, CharityCampaignStartEvent, CharityCampaignStopEvent, CharityDonationEvent, ChannelSubscriptionEndEvent, ChannelSubscriptionGiftEvent, ChannelSubscriptionMessageEvent, ChannelShoutoutCreateEvent, ChannelShoutoutReceiveEvent, ChannelCheerEvent,ChannelPointsAutomaticRewardRedemptionAddEvent
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from typing import Tuple, Optional
import os
from dotenv import load_dotenv
import logging#.config
import colorlog
import twitch_event_handler as teh
import twitch_event_handler_clean as cli_handler
import authscopes as auth_scope
from twitchAPI.type import TwitchBackendException
import db.mydb as mydb
import asyncio
import snafu_event_handler as seh
import traceback
from typing import Union, cast
class TwitchEvents:
    """
    Connects to Twitch-Event-Sub via websockets
    use .env for credentials and other settings

    (c) ChaosQueen 5n4fu
    """
    
    twitch: Optional[Twitch]                = None
    eventsub: Optional[EventSubWebsocket]   = None
    user: Optional[TwitchUser]              = None



    def __init__(self, dotenv_path, use_cli):
        
        self.logger = logging.getLogger(__name__)
        self.add_logger_handler()
        self.logger.setLevel(logging.DEBUG)
        
        self.eventmap = self.get_eventmap()
        self.eventmap_mat = self.get_eventmap_mat()

        load_dotenv(dotenv_path=dotenv_path)
        self.setEnv()
    
            
    async def __aenter__(self):
        
        if self.use_cli_conn:
            self.eventsub, self.twitch, self.user = await self.climockingConn()
        else:
            self.eventsub, self.twitch, self.user = await self.prodConn()
        
        self.eventsub.start()

    async def __aexit__(self, exc_type, exc, tb):
        # ??? deconstructor - shoutout
        await self.eventsub.stop()
        await self.twitch.close()
        self.logger.debug("aexit")
        return self
    
    def add_logger_handler(self):
        handler = colorlog.StreamHandler()
        formatter = colorlog.ColoredFormatter(
            '%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        

    def setEnv(self):
        """
        loads the .env variables
        adjust variables in .env File 
        """
        env_path = find_env()
        print ( dotenv_path )
        if self.use_cli_conn:
            self.TWITCH_CLI_MOCK_API_URL    = os.getenv("TWITCH_CLI_MOCK_API_URL", "BASE_URL not found") 
            self.AUTH_BASE_URL              = os.getenv("AUTH_BASE_URL", "BASE_URL not found")
            self.TWITCH_CLI_CONNECTION_URL  = os.getenv("TWITCH_CLI_CONNECTION_URL", "BASE_URL not found")
            self.TWITCH_SUBSCRIPTION_URL    = os.getenv("TWITCH_SUBSCRIPTION_URL", "SUBSCRIPTION_URL")
            self.CLI_CLIENT_SECRET          = os.getenv("CLI_CLIENT_SECRET", "CLI_S not found")
            self.CLI_USER_ID                = os.getenv("CLI_USER_ID", "CLI_UID not found")
            self.CLI_CLIENTID               = os.getenv("CLI_ID", "CLI_ID not found")


        else:
            self.CLIENT_ID          = os.getenv("CLIENT_ID", "CLIENT_ID not found")
            self.CLIENT_S           = os.getenv("CLIENT_S", "CLIENT_S not found")
            #self.logger.debug(f'CLIENT_ID: {self.BASE_URL or "NOT SET"}')
            #self.logger.debug(f'CLIENT_S: {self.AUTH_BASE_URL or "NOT SET"}')
    

    
    
    def get_eventmap(self):
        return     { 
        ChannelSubscribeEvent: "twitch_subscribe_event",
        ChannelSubscriptionEndEvent:"twitch_subscribe_event",
        ChannelSubscriptionGiftEvent:"twitch_subscribe_event",
        ChannelSubscriptionMessageEvent:"twitch_subscribe_event",
        ChannelRaidEvent:"twitch_action_event",
        ChannelFollowEvent:"twitch_action_event",
        ChannelCheerEvent:"twitch_action_event",ChannelCheerEvent:"twitch_action_event",
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
        } 
  
    async def unifiy_twitch_event(self, x: Union[ChannelSubscribeEvent]):
        event_source = "twitch_event"
        ts = datetime.datetime.now()
        data = ""
        if self.eventmap[type(x)] != None:
            x = cast(ChannelSubscribeEvent, x)
            data = {
                "timestamp": ts, 
                "event_source": event_source,
                "type": self.eventmap[type(x)],
                "data": x.to_dict()
            }
            dispatch(self.eventmap[type(x)], data)
    
   
    async def prodConn(self) -> Tuple[EventSubWebsocket, Twitch, TwitchUser]:
        """
        creates a connection to Twitch EventSub using websockets
        u need a app registered at twitch -> .env
        """
        twitch = await Twitch(self.CLIENT_ID, self.CLIENT_S,)
        helper = UserAuthenticationStorageHelper(twitch, auth_scope.TARGET_SCOPES)
        await helper.bind()
        user = await first(twitch.get_users())

        
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
        self.logger.critical("a worm inserted your console")
        twitch = await Twitch(self.CLI_ID,
                            self.CLI_S,
                            base_url        = self.BASE_URL, 
                            auth_base_url   = self.AUTH_BASE_URL)
        twitch.auto_refresh_auth = False # cli needs no refreshing
        auth = UserAuthenticator(twitch, 
                                 auth_scope.CLI_SCOPES, 
                                 auth_base_url=self.AUTH_BASE_URL)
        x = self.CLI_UID

        token = await auth.mock_authenticate(self.CLI_UID)
        await twitch.set_user_authentication(token,
                                             auth_scope.CLI_SCOPES)
        user = await first(twitch.get_users())
        eventsub = EventSubWebsocket(twitch,
                                    connection_url=self.CONNECTION_URL,
                                    subscription_url=self.SUBSCRIPTION_URL)
        
        return eventsub, twitch, user
    

         
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
        streamonline_id     = await self.eventsub.listen_stream_online(self.user.id,
                                                                       self.on_twitch_event)  
        streamoffline_id    = await self.eventsub.listen_stream_offline(self.user.id,
                                                                        self.on_twitch_event)   
        channelupdatev2_id  = await self.eventsub.listen_channel_update_v2(self.user.id,
                                                                           self.on_twitch_event)
        channelupdate_id    = await self.eventsub.listen_channel_update(self.user.id,
                                                                        self.on_twitch_event)
        
        self.sub_id_map.update({"stream.online": streamonline_id})
        self.sub_id_map.update({"stream.offline": streamoffline_id})
        self.sub_id_map.update({"channel.update_v2": channelupdatev2_id})
        self.sub_id_map.update({"channel.update": channelupdate_id})
        self.logger.info("successfully subscribed to stream_info_events")
    
    async def listen_channel_goal_events(self):
        """
        channel.goal.begin
        channel.goal.end 
        channel.goal.progress
        """

        goal_begin_id       = await self.eventsub.listen_goal_begin(self.user.id, self.on_twitch_event)
        goal_end_id         = await self.eventsub.listen_goal_end(self.user.id, self.on_twitch_event)
        goal_progress_id    = await self.eventsub.listen_goal_progress(self.user.id, self.on_twitch_event)

        self.logger.info("successfully subscribed to channel_goal_events")

        self.sub_id_map.update({"channel.goal.begin": goal_begin_id})
        self.sub_id_map.update({"channel.goal.end": goal_end_id})
        self.sub_id_map.update({"channel.goal.progress": goal_progress_id})

    async def listen_channel_polls(self):
        """
        channel.poll.begin 
        channel.poll.end
        channel.poll.progress   
        """
        poll_begin_id       = await self.eventsub.listen_channel_poll_begin(self.user.id, self.on_twitch_event) 
        poll_end_id         = await self.eventsub.listen_channel_poll_end(self.user.id, self.on_twitch_event)
        poll_progress_id    = await self.eventsub.listen_channel_poll_progress(self.user.id, self.on_twitch_event)

        self.logger.info("successfully subscribed to channel_poll_events")

        self.sub_id_map.update({"channel.poll.begin": poll_begin_id})
        self.sub_id_map.update({"channel.poll.end": poll_end_id})
        self.sub_id_map.update({"channel.poll.progress": poll_progress_id})

    async def listen_channel_predictions(self):
        """
        channel.prediction.begin
        channel.prediction.end
        channel.prediction.lock
        channel.prediction.progress
        """

        prediction_begin_id         = await self.eventsub.listen_channel_prediction_begin(self.user.id, self.on_twitch_event)
        prediction_end_id           = await self.eventsub.listen_channel_prediction_end(self.user.id, self.on_twitch_event)
        prediction_lock_id          = await self.eventsub.listen_channel_prediction_lock(self.user.id, self.on_twitch_event)
        prediction_progress_id      = await self.eventsub.listen_channel_prediction_progress(self.user.id, self.on_twitch_event)

        self.logger.info("successfully subscribed to channel_prediction_events")

        self.sub_id_map.update({"channel.prediction.begin": prediction_begin_id})
        self.sub_id_map.update({"channel.prediction.end": prediction_end_id})
        self.sub_id_map.update({"channel.prediction.lock": prediction_lock_id})
        self.sub_id_map.update({"channel.prediction.progress": prediction_progress_id})

    async def listen_channel_points(self):
        """
        channel.channel_points_custom_reward.add 
        channel.channel_points_custom_reward.remove 
        channel.channel_points_custom_reward.update 
        channel.channel_points_custom_reward_redemption.add
        channel.channel_points_custom_reward_redemption.update
        """
        try:
            reward_add_id        = await self.eventsub.listen_channel_points_custom_reward_add(self.user.id, self.on_twitch_event)
            reward_remove_id     = await self.eventsub.listen_channel_points_custom_reward_remove(self.user.id, self.on_twitch_event)
            reward_update_id     = await self.eventsub.listen_channel_points_custom_reward_update(self.user.id, self.on_twitch_event)
            redemption_add_id    = await self.eventsub.listen_channel_points_custom_reward_redemption_add(self.user.id, self.on_twitch_event)
            redemption_update_id = await self.eventsub.listen_channel_points_custom_reward_redemption_update(self.user.id, self.on_twitch_event)
            #auto_reward_redemption = await self.eventsub.listen_channel_points_automatic_reward_redemption_add(self.user.id, self.on_twitch_event)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
        

        self.sub_id_map.update({"channel.channel_points_custom_reward.add": reward_add_id})
        self.sub_id_map.update({"channel.channel_points_custom_reward.remove": reward_remove_id})
        self.sub_id_map.update({"channel.channel_points_custom_reward.update": reward_update_id})
        self.sub_id_map.update({"channel.channel_points_custom_reward_redemption.add": redemption_add_id})
        #self.sub_id_map.update({"channel.channel_points_custom_reward_redemption.update": redemption_update_id})


        self.logger.info("successfully subscribed to channel_point_events")


    async def listen_hype_train(self):
        """
        channel.hype_train.begin 
        channel.hype_train.end 
        channel.hype_train.progress
        """

        hype_train_begin_id    = await self.eventsub.listen_hype_train_begin(self.user.id, self.on_twitch_event)
        hype_train_end_id      = await self.eventsub.listen_hype_train_end(self.user.id, self.on_twitch_event)
        hype_train_progress_id = await self.eventsub.listen_hype_train_progress(self.user.id, self.on_twitch_event)

        self.logger.info("successfully subscribed to hype_train_events")

        self.sub_id_map.update({"channel.hype_train.begin": hype_train_begin_id})
        self.sub_id_map.update({"channel.hype_train.end": hype_train_end_id})   
        self.sub_id_map.update({"channel.hype_train.progress": hype_train_progress_id})

    async def listen_ban_events(self):
        """
        ATTENTION: PROBABLY NOT WORKING WITHIN CLI!


        channel.ban 
        channel.unban
        channel.unban_request.create
        channel.unban_request.resolve
        TODO: mod? ->


        """
        ban_id                = await self.eventsub.listen_channel_ban(self.user.id, self.on_twitch_event)
        unban_id              = await self.eventsub.listen_channel_unban(self.user.id, self.on_twitch_event)
        unban_request_id      = await self.eventsub.listen_channel_unban_request_create(self.user.id, self.user.id, self.on_twitch_event)
        unban_request_resolve = await self.eventsub.listen_channel_unban_request_resolve(self.user.id, self.user.id, self.on_twitch_event)

        self.logger.info("successfully subscribed to ban_events")

        self.sub_id_map.update({"channel.ban": ban_id})
        self.sub_id_map.update({"channel.unban": unban_id})
        self.sub_id_map.update({"channel.unban_request.create": unban_request_id})
        self.sub_id_map.update({"channel.unban_request.resolve": unban_request_resolve})



    async def listen_charity_events(self):
        """
        channel.charity_campaign.donate 
        channel.charity_campaign.progress
        channel.charity_campaign.start 
        channel.charity_campaign.stop
        """
        charity_donate_id   = await self.eventsub.listen_channel_charity_campaign_donate(self.user.id, self.on_twitch_event)
        charity_progress_id = await self.eventsub.listen_channel_charity_campaign_progress(self.user.id, self.on_twitch_event)
        charity_start_id    = await self.eventsub.listen_channel_charity_campaign_start(self.user.id, self.on_twitch_event)
        charity_stop_id     = await self.eventsub.listen_channel_charity_campaign_stop(self.user.id, self.on_twitch_event)

        self.logger.info("successfully subscribed to charity_events")

        self.sub_id_map.update({"channel.charity_campaign.donate": charity_donate_id})
        self.sub_id_map.update({"channel.charity_campaign.progress": charity_progress_id})
        self.sub_id_map.update({"channel.charity_campaign.start": charity_start_id})
        self.sub_id_map.update({"channel.charity_campaign.stop": charity_stop_id})

    async def listen_shoutout_events(self):
        """
        channel.shoutout.create
        channel.shoutout.receive
        """
        shoutout_create_id  = await self.eventsub.listen_channel_shoutout_create(self.user.id, self.user.id, self.on_twitch_event)
        shoutout_receive_id = await self.eventsub.listen_channel_shoutout_receive(self.user.id, self.user.id,  self.on_twitch_event)

        self.logger.info("successfully subscribed to shoutout_events")

        self.sub_id_map.update({"channel.shoutout.create": shoutout_create_id})
        self.sub_id_map.update({"channel.shoutout.receive": shoutout_receive_id})

    async def listen_subscribe_events(self):
        """
        channel.subscribe
        channel.subscription.end
        channel.subscription.gift0
        channel.subscription.message
        """
        subscribe_id          = await self.eventsub.listen_channel_subscribe(self.user.id, self.on_twitch_event)
        sub_end_id            = await self.eventsub.listen_channel_subscription_end(self.user.id, self.on_twitch_event)
        sub_gift_id           = await self.eventsub.listen_channel_subscription_gift(self.user.id, self.on_twitch_event)
        sub_message_id        = await self.eventsub.listen_channel_subscription_message(self.user.id, self.on_twitch_event)

        self.logger.info("successfully subscribed to subscribe_events")
        self.logger.debug(f'sub_gift_id: {sub_gift_id}\tsub_message_id: {sub_message_id}\tsub_end_id: {sub_end_id}')
        self.sub_id_map.update({"channel.subscribe": subscribe_id})
        self.sub_id_map.update({"channel.subscription.end": sub_end_id})
        self.sub_id_map.update({"channel.subscription.gift": sub_gift_id})
           
            
            # The combination of values in the type and version fields is not valid
            #sub_message_id = await self.eventsub.listen_channel_chat_message(self.user.id , self.user.id, self.onChatMessage)
            #The combination of values in the type and version fields is not validcription.gift": sub_gift_id})
        self.sub_id_map.update({"channel.subscription.message": sub_message_id})

    async def listen_moderate_events(self):
        """
        channel.moderator.add 
        channel.moderator.remove
        channel.ad_break.begin 
        """
        mod_add_id          = await self.eventsub.listen_channel_moderator_add(self.user.id, self.on_twitch_event)
        mod_remove_id       = await self.eventsub.listen_channel_moderator_remove(self.user.id, self.on_twitch_event)
        ad_break_begin_id   = await self.eventsub.listen_channel_ad_break_begin(self.user.id, self.on_twitch_event)

        self.logger.info("successfully subscribed to moderate_events")

        self.sub_id_map.update({"channel.moderator.add": mod_add_id})
        self.sub_id_map.update({"channel.moderator.remove": mod_remove_id})
        self.sub_id_map.update({"channel.ad_break.begin": ad_break_begin_id})

    async def listen_channel_action_events(self):
        """
        channel.cheer 
        channel.follow 
        channel.raid 
        """

        self.logger.info(f'copy&paste the following command to trigger an event')
        #sub_id = await self.eventsub.listen_channel_subscribe(self.user.id, self.on_twitch_event)
        raid_id = await self.eventsub.listen_channel_raid(self.on_twitch_event, 
                                                        None,self.user.id)
        follow_id = await self.eventsub.listen_channel_follow_v2(self.user.id, 
                                                                self.user.id, 
                                                                self.on_twitch_event)
        self.logger.debug(f'twitch event trigger channel.follow -t {self.user.id} -u {follow_id} -T websocket') 
        #self.logger.debug(f'twitch event trigger channel.subscribe -t {self.user.id} -u {sub_id} -T websocket') 
        self.logger.debug(f'twitch event trigger channel.raid -t {self.user.id} -u {raid_id} -T websocket') 
        #self.sub_id_map.update({"channel.subscribe": sub_id})
        self.sub_id_map.update({"channel.raid": raid_id})

        self.sub_id_map.update({"channel.follow": follow_id})
        sub_message_id = await self.eventsub.listen_channel_cheer(self.user.id, self.on_twitch_event)
        self.sub_id_map.update({"channel.cheer": sub_message_id})

        """
                raid_id = await self.eventsub.listen_channel_raid(self.on_twitch_event, 
                                                                None,self.user.id)
                follow_id = await self.eventsub.listen_channel_follow_v2(self.user.id, 
                                                                        self.user.id, 
                                                                        self.on_twitch_event)
                sub_message_id = await self.eventsub.listen_channel_cheer(self.user.id, self.on_twitch_event)
                
                self.sub_id_map.update({"channel.raid": raid_id})
                self.sub_id_map.update({"channel.follow": follow_id})
                self.sub_id_map.update({"channel.cheer": sub_message_id})
                
                self.logger.debug(f'twitch event trigger channel.follow -t {self.user.id} -u {follow_id} -T websocket') 
        """


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
