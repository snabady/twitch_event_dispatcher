import mysql.connector
from datetime import datetime




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
    insert_query =  """
                    INSERT INTO followerlist (user_id, user_name, user_login, followed_at)
                    VALUES (%s, %s, %s, %s)
                    """
    cursor.execute(insert_query, (follower.get("user_id"), follower.get("user_name"), follower.get("user_login") , follower.get("followed_at")))
    conn.commit()

    cursor.close()
    conn.close()

def handle_stwitch_streaminfo_event(event: dict):
    pass    
