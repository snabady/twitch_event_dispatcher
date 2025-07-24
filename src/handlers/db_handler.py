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


def execute_query(query: str, values: []) -> bool:
    conn = get_db_conn()
    cursor = conn.cursor()

    # TODO check return...
    ret = cursor.execute(query, values)

    conn.commit()
    cursor.close()
    conn.close()

    return ret 


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

def write_cli_params(cli_ids):
    conn = get_db_conn()
    cursor = conn.cursor()

    query = "delete from cli_sub_ids;"
    cursor.execute(query)
    conn.commit()
    data = [(name, id) for name, id in cli_ids.items()]
    cursor.executemany("INSERT INTO cli_sub_ids (cli_command_name, cli_command_id) VALUES (%s,%s)", data)
    conn.commit()
    cursor.close()
    conn.close()
    
def get_chat_commands():
    logger.debug("get_chat_command")
    conn = get_db_conn()
    cursor = conn.cursor()
    query = "SELECT chat_command, params, command_type FROM chat_command WHERE is_active=1"
    cursor.execute(query)
    
    return cursor.fetchall()


def insert_stream_stats(db_values):
    conn = get_db_conn()
    cursor = conn.cursor()
    column_names = get_table_column_names("stream_stats", "twitch")
    logger.debug(f"stream_stats, twitch: {len(column_names)} {len(db_values)} \n\n{db_values}\n\n{column_names} ")
    s_ = ', '.join(['%s'] * len(db_values))

    query = f"""INSERT INTO stream_stats (stream_date, 
                                        total_chat_messages, 
                                        new_subscribers, 
                                        new_follower, 
                                        new_chatters, 
                                        channel_joins, 
                                        first_messages, 
                                        unique_viewer_count, 
                                        total_channel_joins, 
                                        daily_messages, 
                                        total_subs, 
                                        total_follower, 
                                        raids_received) 
            VALUES ({s_})"""

    cursor.execute(query,db_values) 
    print(f"{cursor.statement}")
    conn.commit() 
    cursor.close()
    conn.close()


def get_table_column_names(table: str, schema: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    query = f"""SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table}' and table_schema='{schema}'"""
    cursor.execute(query)
    ret = cursor.fetchall()
    cursor.close()
    conn.close()
    return ret




def get_stats_columns():
    conn = get_db_conn()
    cursor = conn.cursor()
    query = """SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'stream_stats' and table_schema='twitch'"""
    cursor.execute(query)
    ret = cursor.fetchall()
    cursor.close()
    conn.close()
    return ret

def get_active_channelpoint_rewards():
    conn = get_db_conn()
    cursor = conn.cursor()
    query ="SELECT id,name,params from custom_rewards where active=1"
    cursor.execute(query)
    ret =  cursor.fetchall()
    cursor.close()
    conn.close()
    return ret

def select_something(query: str) :
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute(query)
    ret = cursor.fetchall()
    cursor.close()
    conn.close()
    return ret
