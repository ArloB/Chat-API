'''Standup functions'''
from time import time
import threading
from helper_functions import token_validation
from message import message_send
from error import AccessError, InputError
from auth import decode_token
from user import user_profile
from db import db

def __standup_finish(token, channel_id):
    msg = db['channels'][channel_id].get('standup_msg', '').rstrip()
    if msg != '':
        message_send(token, channel_id, msg)
    db['channels'][channel_id]['standup_active'] = False
    db['channels'][channel_id]['standup_time'] = None
    db['channels'][channel_id]['standup_msg'] = ''
    

def standup_start(token, channel_id, length):
    '''Start a standup in given channel. Returns ending time'''
    if not token_validation(token):
        raise AccessError(description="Invalid token")
    
    if not channel_id in db['channels']:
        raise InputError(description="Invalid Channel ID")

    if db['channels'][channel_id].get('standup_active', False):
        raise InputError(description="Standup already active")

    db['channels'][channel_id]['standup_active'] = True

    t = threading.Timer(length, __standup_finish, args=(token, channel_id,))
    
    fin = time() + length
    t.start()

    db['channels'][channel_id]['standup_time'] = fin
    return {'time_finish': int(fin)}


def standup_active(token, channel_id):
    '''Returns whether there is a current standup going on and what time it ends'''
    if not token_validation(token):
        raise AccessError(description="Invalid token")

    if not db['channels'].get(channel_id, False):
        raise InputError(description="Invalid Channel ID")

    standup_time = db['channels'][channel_id].get('standup_time')
    fin = int(standup_time) if standup_time is not None else standup_time

    return {
        'is_active': db['channels'][channel_id].get('standup_active', False),
        'time_finish': fin
    }


def standup_send(token, channel_id, message):
    '''Adds given message to standup queue in given channel'''
    if not token_validation(token):
        raise AccessError(description="Invalid token")

    if not channel_id in db['channels']:
        raise InputError(description="Invalid Channel ID")

    if decode_token(token) not in db['channels'][channel_id]['all_members']:
        raise AccessError(description="The authorised user is not a member of the channel that the message is within")

    if not db['channels'][channel_id].get('standup_active', False):
        raise InputError(description="Standup not active")

    if len(message) > 1000:
        raise InputError(description="Message is more than 1000 characters")

    handle = user_profile(token, decode_token(token))['user']['handle_str']
    db['channels'][channel_id]['standup_msg'] = db['channels'][channel_id]['standup_msg'] \
        + f"{handle}: {message}\n" if 'standup_msg' in db['channels'][channel_id] else f"{handle}: {message}\n"
    
    return {}