import os
import mysql.connector
from mysql.connector import pooling, Error
import logging
import datetime
from src.utils import log
from datetime import datetime
from src.dispatcher.event_dispatcher import post_event
from src.handlers import twitchapi 
logger = logging.getLogger("DB_LOG")
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   

_pool: pooling.MySQLConnectionPool = None

def init_db_pool():
    
    global _pool
    if _pool is not None:
        return

    host_       = os.getenv("DB_HOST")
    user_       = os.getenv("DB_USER")
    passw_      = os.getenv("DB_PASS")
    database_   = os.getenv("DB_DATABASE")
    pool_size   = int(os.getenv("DB_POOL_SIZE", "5"))
    pool_name   = os.getenv("DB_POOL_NAME")

    _pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            host=host_,
            user=user_,
            password=passw_,
            database=database_,
            pool_reset_session=True,
            )

    conn =  mysql.connector.connect(
        host=host_,      
        user=user_,  
        password=passw_,
        database=database_
    )

def get_db_conn():
    global _pool
    if _pool is None:
        init_db_pool()
    try:
        return _pool.get_connection()
    except Error as e:
        logger.exception("Failed to get connection from pool, attempting re-init")
        init_db_pool()
        return _pool.get_connection()


def execute_query(query: str, values=None):
    """
    Execute a query using a pooled connection.
    - For SELECT queries returns fetched rows (list of tuples).
    - For non-SELECT queries returns affected rowcount.
    Values can be None or a sequence/mapping for parameterized queries.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        if values is None:
            cursor.execute(query)
        else:
            cursor.execute(query, values)

        if query.strip().lower().startswith("select"):
            ret = cursor.fetchall()
        else:
            conn.commit()
            ret = cursor.rowcount
        print(cursor.statement)
        return ret
    except Exception:
        logger.exception("Error executing query")
        logger.exception(cursor.statement)
        raise
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                logger.exception("Failed to close cursor")
        if conn:
            try:
                conn.close()  # returns connection to pool
            except Exception:
                logger.exception("Failed to close/return connection")


def check_excisting_twitch_user(user_name):
    query = """
            SELECT user_id from twitch_users where user_name = %s
    """

    ret = execute_query(query, [user_name])
    logger.debug(ret)
    for x in ret:
        logger.debug(x)

def add_new_twitch_user(user_data):
   # user_id	user_name	user_displayname	followed_at	account_created	type	description	profile_image_url	offline_image_url	view_count	created_at 
    logger.debug(f"user_data:{len(user_data)} |  {user_data}")
    query = f"""
                        INSERT INTO twitch_users(user_id, 
                                                        user_name, 
                                                        user_displayname,
                                                        account_created, 
                                                        type, 
                                                        description, 
                                                        profile_image_url,
                                                        offline_image_url, 
                                                        view_count,
                                                        followed_at
                                                        )
                        VALUES (%s, %s, %s,  %s, %s, %s, %s, %s,  %s, {datetime.now()})
                        ON DUPLICATE KEY UPDATE
                        USER_ID             = values(user_id),
                        user_name           = values(user_name),
                        user_displayname    = values(user_displayname),
                        type                = values(type),
                        description         = values(description),
                        profile_image_url   = values(profile_image_url),
                        account_created     = values(account_created),
                        view_count          = values(view_count),
                        offline_image_url   = values(offline_image_url)

                        """

    execute_query(query, user_data)

def update_special_users(data,is_vip=0):
    query=f"""
            INSERT INTO special_users (user_id, is_vip, user_login, user_name, vip_since,epaper_id)
            VALUES(%s,%s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
            user_id     = VALUES(user_id),
            is_vip      = VALUES(is_vip), 
            user_login  = VALUES(user_login),
            user_name   = VALUES(user_name)
    """
    print (query)
    execute_query(query,data)

def remove_from_followerlist(user_id):
    query =f"delete from followerlist where user_id = {user_id}"
    execute_query(query,None)

def update_current_follower(user_ids):
    logger.debug("in update current follower, deleting followerlist and inserting fresh, received")
    query = "DELETE FROM current_followers"
    execute_query(query,None)
    values  =",".join([f"({user_id})" for user_id in user_ids])
    query = f"""    INSERT INTO current_followers (user_id) values {values} """
    execute_query(query,None)

def insert_new_follower(userdata):
    query = f"insert into followerlist  (user_id, followed_at) values (%s,%s)"
    execute_query(query, userdata)

def insert_new_follwer(follower:dict) -> str:
    conn = get_db_conn()
    cursor = conn.cursor()
    # "upsert" only insert if no user_id exists -> userid==unique
    insert_user_query = """
                        INSERT IGNORE INTO twitch_users(user_id, 
                                                        user_name, 
                                                        user_displayname)
                        VALUES (%s, %s, %s)
                        """
    cursor.execute(insert_user_query, (follower.get("user_id"), 
                                       follower.get("user_login"),
                                       #user_loginfollower.get("user_name"),
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

def add_unfollow(user_id: int):
    query ="INSERT INTO unfollow_events (user_id, unfollowed_at) VALUES (%s, %s)"
    execute_query(query, [user_id, datetime.now()])

def handle_get_followage_by_user(user_name: dict):
    logger.debug("handle_get_followage by user")
    logger.debug(f"user_name: {user_name}, type: {type(user_name)}")
    conn = get_db_conn()
    cursor = conn.cursor()
    user_name = user_name.get("user_name")
    twitchapi.trigger_get_user_id(str(user_name))

    
    # get user_id since user_name could have changed.... we need current user_id
   # post_event("twapi_get_user_id", {"event_type": "twapi_get_user_id",
    #                                 "event_data": { "user_name": user_name}})

def handle_get_followage(user_id: int):
    logger.debug("handle_get_followage ")
    logger.debug(f"user_name: {user_id}")
    print("blub blub blub.............")
    conn = get_db_conn()
    cursor = conn.cursor()
    #user_id = user_id.get("user_id")
    query = f"SELECT user_name, followed_at FROM twitch_users WHERE user_id = {user_id}"
    cursor.execute(query, None)
    result =cursor.fetchone()
    logger.debug(result)
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

def insert_bait_stats(db_values):
    conn = get_db_conn()
 
    for user in db_values:
       logger.debug(f"{user}")
       user.append(datetime.now())
       cursor = conn.cursor()
       query = f"""
                    INSERT INTO bait_history ( user_name,
                                               bait_counter,
                                               jebaited,
                                               total_weight, 
                                               bait_date)
                    VALUES (%s,%s,%s,%s,%s)
                """
       cursor.execute(query, user)
       logger.debug(f"{cursor.statement}")
       conn.commit()
       cursor.close()
    conn.close()


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
def update_current_mods(mods: list):
    conn = get_db_conn()
    cursor =conn.cursor()

    for x in mods:
        
        query = """
            INSERT INTO special_users (user_id, user_login, user_name,  vip_since)
            SELECT u.user_id, %s, %s,  0, %s
            FROM twitch_users u
            WHERE u.user_id = %s
        """
        cursor.execute(query, [ x.user_login, x.user_name, datetime.now(), x.user_id])
        print(f"{cursor.statement}")
    conn.commit()
    cursor.close()
    conn.close()


def make_epaper_user_data():
    user_data =[]
    update_current_vips() # 

def update_current_vips(vips: list):
    conn = get_db_conn()
    cursor =conn.cursor()
    logger.debug(f"vips: {vips}")
    for x in vips:
        logger.debug(f"vip: {x}")
        query = """
            INSERT INTO special_users (user_id,is_vip, user_login, user_name, vip_since,epaper_id) 
            SELECT u.user_id, %s,%s, %s, %s, %s
            FROM twitch_users u
            WHERE u.user_id = %s
            ON DUPLICATE KEY UPDATE
            is_vip      = values(is_vip),
            user_login  = values(user_login),
            user_name   = values(user_name),
            vip_since   = values(vip_since),
            epaper_id   = values(epaper_id)

        """
        #execute_query(query, [ 1, x.user_login,  x.user_name,  datetime.now(),x.user_id])
        execute_query(query, x)
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

def update_current_channelpoint_reward(rewards):
    for reward in rewards:
        key_val = [reward.title,# same as name
                      reward.title, 
                      reward.id,
                      reward.is_enabled, # active in db
                      reward.background_color, 
                      reward.is_enabled, 
                      reward.cost, 
                      reward.prompt, 
                      reward.is_user_input_required, 
                      #reward.max_per_user_per_stream_setting, 
                      #      reward.global_cooldown_setting, 
                      reward.is_paused,
                      reward.is_in_stock,
                      #reward.default_image, 
                      reward.should_redemptions_skip_request_queue,
                      reward.redemptions_redeemed_current_stream, 
                      reward.cooldown_expires_at]
        query = f""" 
                insert into custom_rewards (name, 
                                            title, 
                                            id,
                                            active,
                                            background_color, 
                                            is_enabled, 
                                            cost, 
                                            prompt, 
                                            is_user_input_required,
                                            is_paused,
                                            is_in_stock,
                                            should_redemptions_skip_request_queue,
                                            redemptions_redeemed_current_stream,
                                            cooldown_expires_at)
                values ({', '.join('%s' for _ in key_val)})
                ON DUPLICATE KEY UPDATE
                    name                                    = values(name),
                    id                                      = values(id), 
                    active                                  = values(active),
                    title                                   = values(title),
                    background_color                        = values(background_color),
                    is_enabled                              = values(is_enabled),
                    cost                                    = values(cost),
                    prompt                                  = values(prompt),
                    is_user_input_required                  = values(is_user_input_required),
                    is_paused                               = values(is_paused),
                    is_in_stock                             = values(is_in_stock),
                    should_redemptions_skip_request_queue   = values(should_redemptions_skip_request_queue),
                    redemptions_redeemed_current_stream     = values(redemptions_reedemed_current_stream),
                    cooldown_expires_at                     = values(cooldown_expires_at)
                """
    #    print (query)
        ret = execute_query(query, key_val) 

def select_something(query: str) :
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute(query)
    ret = cursor.fetchall()
    cursor.close()
    conn.close()
    return ret
