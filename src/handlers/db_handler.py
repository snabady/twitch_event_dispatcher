import mysql.connector
import logging
from utils import log
from datetime import datetime
from dispatcher.event_dispatcher import post_event

from handlers import twitchapi #import trigger_get_user_id
logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   


"""event_types = {
            "stream.online": handle_stream_online,
            "stream.offline": handle_stream_offline,
            "channel.update_v2": handle_channel_update_v2,
            "channel.update": handle_channel_update
        }"""

def get_db_conn():
    conn =  mysql.connector.connect(
        host="localhost",      
        user="root",  
        password="example",
        database="twitch"
    )
    return conn

def insert_new_follwer(follower:dict) -> str:
    conn = get_db_conn()
    cursor = conn.cursor()
    # "upsert" only insert if no user_id exists -> userid==unique
    insert_user_query = """
                        INSERT IGNORE INTO twitch_users(user_id, 
                                                        user_name, 
                                                        user_displayname, 
                                                        followed_at)
                        VALUES (%s, %s, %s, %s)
                        """
    cursor.execute(insert_user_query, (follower.get("user_id"), 
                                       follower.get("user_login"),
                                       follower.get("user_name"),
                                       follower.get("followed_at")))
    conn.commit()
    insert_query =  """
                    INSERT IGNORE INTO followerlist (user_id, followed_at)
                    VALUES (%s, %s)
                    """
    cursor.execute(insert_query, (follower.get("user_id"), 
                                  follower.get("followed_at")))
    conn.commit()

    cursor.close()
    conn.close()

def handle_stwitch_streaminfo_event(event: dict):
    pass    


def handle_get_followage_by_user(user_name: str):
    logger.debug("handle_get_followage by user")
    logger.debug(f"user_name: {user_name}")
    conn = get_db_conn()
    cursor = conn.cursor()
    #user_name = user_name.get("user_name")
    twitchapi.trigger_get_user_id(user_name)

    
    # get user_id since user_name could have changed.... we need current user_id
    #post_event("twapi_get_user_id", {"event_type": "twapi_get_user_id",
    #                                 "event_data": { "user_name": user_name}})

def handle_get_followage(user_id: int):
    logger.debug("handle_get_followage ")
    logger.debug(f"user_name: {user_id}")
    conn = get_db_conn()
    cursor = conn.cursor()
    #user_id = user_id.get("user_id")
    query = "SELECT user_name, followed_at FROM twitch_users WHERE user_id = %s"
    cursor.execute(query,( user_id, ))

    result = cursor.fetchone()
    if result:
        message = f" {result[0]} following since: {result[1]}"
        post_event("irc_send_message", message)
    else: 
        post_event("irc_send_message", "moep, what about a follow first?")


    cursor.close()
    conn.close()

def get_chat_commands():
    logger.debug("get_chat_command")
    conn = get_db_conn()
    cursor = conn.cursor()
    query = "SELECT chat_command FROM chat_command WHERE is_active=1"
    cursor.execute(query)
    
    return cursor.fetchall()