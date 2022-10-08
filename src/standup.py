'''Standup functions'''
from calendar import c
from time import time
import threading
from db import get_db
from helper_functions import get_u_id, token_validation
from message import message_send
from error import AccessError, InputError
from user import user_profile

db = get_db()

standups = {}

def __standup_finish(token, channel_id):
    msg = standups[channel_id].get('standup_msg', '').rstrip()
    
    if msg != '':
        message_send(token, channel_id, msg)
    
    standups[channel_id].clear()
    

def standup_start(token, channel_id, length):
    '''Start a standup in given channel. Returns ending time'''
    if not token_validation(token):
        raise AccessError(description="Invalid token")
    
    if not channel_id in standups:
        standups[channel_id] = {
            'standup_time': None,
            'standup_msg': ''
        }
    else:
        raise InputError(description="Standup already active")

    t = threading.Timer(length, __standup_finish, args=(token, channel_id,))
    
    fin = time() + length
    t.start()

    standups[channel_id]['standup_time'] = fin
    return {'time_finish': int(fin)}


def standup_active(token, channel_id):
    '''Returns whether there is a current standup going on and what time it ends'''
    if not token_validation(token):
        raise AccessError(description="Invalid token")

    active = standups.get(channel_id, False)

    if active:
        standup_time = standups[channel_id].get('standup_time')
        fin = int(standup_time) if standup_time is not None else standup_time
    else:
        fin = None
    
    return {
        'is_active': active,
        'time_finish': fin
    }


def standup_send(token, channel_id, message):
    '''Adds given message to standup queue in given channel'''
    user_id = get_u_id(token)
    
    if not token_validation(token):
        raise AccessError(description="Invalid token")

    if not channel_id in standups:
        raise InputError(description="Standup not active")

    with db.cursor() as cur:
        cur.execute("select * from channel_users where user_id = %s and channel_id = %s", [user_id, channel_id])
        
        if not cur.rowcount:
            raise AccessError(description="The authorised user is not a member of the channel that the message is within")

    if len(message) > 1000:
        raise InputError(description="Message is more than 1000 characters")

    user = user_profile(token, user_id)
    
    handle = user['user']['handle_str'] if user['user']['handle_str'] else user['user']['name_first']
    
    standups[channel_id]['standup_msg'] = standups[channel_id]['standup_msg'] \
        + f"{handle}: {message}\n" if 'standup_msg' in standups[channel_id] else f"{handle}: {message}\n"
    
    return {}