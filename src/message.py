'''Message functions'''
import time
import threading

from error import InputError, AccessError
from channels import get_u_id, token_validation
from db import db

def create_message(token, channel_id, message, time_sent):
    '''sending a message to a channel'''
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    if len(message) > 1000:
        raise InputError(description='Message too long')

    u_id = get_u_id(token)

    #check if channel id doesn't exist
    if channel_id not in db['channels']:
        raise InputError(description='Invalid Channel')

    if u_id not in db['channels'][channel_id]['all_members']: #check u_id not in channel
        raise AccessError(description='User not in channel')

    # calculate message_id
    if 'deleted_messages' not in db['channels'][channel_id]:
        message_id = channel_id * 10000 + \
        len(db['channels'][channel_id]['messages'])
    else:
        message_id = channel_id * 10000 + \
        len(db['channels'][channel_id]['messages']) + \
        len(db['channels'][channel_id]['deleted_messages'])
    # create dict of message and its details
    message_dict = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_created': time_sent,
        'reacts': [],
        'is_pinned': False
    }
    return message_dict, message_id

def store_message(channel_id, message_dict):
    db['channels'][channel_id]['messages'].append(message_dict)

def message_send(token, channel_id, message):
    message_dict, message_id = create_message(token, channel_id, message, int(time.time()))
    store_message(channel_id, message_dict)

    return {
        'message_id': message_id,
    }

def find_channel(message_id):
    #returns channel_id, iterator in messages, deleted?, valid?
    for ch in db['channels']:
        #loop through each messages dictionary in channel
        for i, _ in enumerate(db['channels'][ch]['messages']):
            if message_id == db['channels'][ch]['messages'][i]['message_id']:
                return ch, i, False, True
        #check if message has been deleted
        if 'deleted_messages' in db['channels'][ch]:
            if message_id in db['channels'][ch]['deleted_messages']:
                return ch, 0, True, False
    return ch, 0, False, False

def message_remove(token, message_id):
    '''removing a message from a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    u_id = get_u_id(token)
    for user in db['accounts']:
        if u_id is db['accounts'][user]['u_id']:
            email = db['accounts'][user]['email']
    owner = db['accounts'][email]['is_owner']

    channel, i, deleted, valid = find_channel(message_id)
    if deleted == True:
        raise InputError(description='Message already deleted')
    elif valid == False:
        raise AccessError(description="Message doesn't exist")
    if owner or u_id in db['channels'][channel]['owner_members'] or \
    u_id == db['channels'][channel]['messages'][i]['u_id']:
        message_list = db['channels'][channel]['messages']
        deleted = message_list.pop(i)
        deleted_m_id = deleted['message_id']
        #add deleted to deleted_messages in channels
        if 'deleted_messages' not in db['channels'][channel]:
            db['channels'][channel]['deleted_messages'] = []
            db['channels'][channel]['deleted_messages'].append(deleted_m_id)
        else:
            db['channels'][channel]['deleted_messages'].append(deleted_m_id)
        return {}

    raise AccessError(description="Cannot delete someone else's message")

def message_edit(token, message_id, message):
    '''editing a message in a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    #get u_id and email from token
    u_id = get_u_id(token)
    for user in db['accounts']:
        if u_id is db['accounts'][user]['u_id']:
            email = db['accounts'][user]['email']
    owner = db['accounts'][email]['is_owner']
    channel, i, deleted, valid = find_channel(message_id)
    if not valid or deleted:
        raise AccessError(description="Message doesn't exist")
    #if flockr owner, owner member of channel or user sent the message
    if owner or u_id in db['channels'][channel]['owner_members'] or \
    u_id == db['channels'][channel]['messages'][i]['u_id']:
        if message == '':
            message_list = db['channels'][channel]['messages']
            message_list.remove(db['channels'][channel]['messages'][i])
        else:
            db['channels'][channel]['messages'][i]['message'] = message
        return {}

    raise AccessError(description="Cannot edit someone else's message")

def message_sendlater(token, channel_id, message, time_sent):
    '''sends message to channel at later time'''
    if time_sent < time.time():
        raise InputError(description='Cannot send message to past')
    message_dict, message_id = create_message(token, channel_id, message, time_sent)
    x = threading.Timer(time_sent-time.time(), store_message, args=[channel_id, message_dict])
    x.start()
    return {
        'message_id': message_id
    }

def message_react(token, message_id, react_id):
    '''Reacting to a message in a channel'''
    if not token_validation(token): #check valid token
        raise AccessError(description='Invalid Token')

    if react_id != 1: #if invalid react_id
        raise InputError(description='Invalid react_id')

    ch, i, deleted, valid = find_channel(message_id)
    if not valid or deleted: #if message id is invalid or has been deleted
        raise InputError(description="Message doesn't exist in channel")

    u_id = get_u_id(token) #get u_id and email from token
    #check if user is part of channel the message is in
    if u_id in db['channels'][ch]['all_members']:
        #if no reacts
        reacts_list = db['channels'][ch]['messages'][i]['reacts']
        if reacts_list == []:
            reacts = {
                'react_id': react_id,
                'u_ids': [u_id],
                'is_this_user_reacted': False
            }
            db['channels'][ch]['messages'][i]['reacts'].append(reacts)
        elif u_id in reacts_list[0]['u_ids']:
            raise InputError(description="Already reacted to message")
        else:
            #append u_id to u_ids
            db['channels'][ch]['messages'][i]['reacts'][0]['u_ids'].append(u_id)
        return {}
    raise InputError(description="Cannot access this channel's messages")

def message_unreact(token, message_id, react_id):
    #check valid token
    if not token_validation(token):
        raise AccessError(description='Invalid Token')
    #if invalid react_id
    if react_id != 1:
        raise InputError(description='Invalid react_id')
    ch, i, deleted, valid = find_channel(message_id)
    #if message id is invalid or has been deleted
    if not valid or deleted:
        raise InputError(description="Message doesn't exist in channel")
    u_id = get_u_id(token) #get u_id and email from token
    #check if user is part of channel the message is in
    if u_id in db['channels'][ch]['all_members']:
        reacts_list = db['channels'][ch]['messages'][i]['reacts']
        if reacts_list == []:
            raise InputError(description='Message does not have a react')
        #if user unreacted to that message, remove u_id from u_ids
        elif u_id in reacts_list[0]['u_ids']:
            for j, user in enumerate(reacts_list[0]['u_ids']): #loop through u_ids
                if u_id == user:
                    db['channels'][ch]['messages'][i]['reacts'][0]['u_ids'].pop(j)
                    reacts_list2 = db['channels'][ch]['messages'][i]['reacts']
                    if len(reacts_list2[0]['u_ids']) == 0: #delete reacts dictionary
                        db['channels'][ch]['messages'][i]['reacts'] = []
            return {}
        else:
            raise InputError(description='Did not react to this message')
    raise InputError(description="Cannot access this channel's messages")

def message_pin(token, message_id):
    '''pins a message in channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError

    #get u_id and email from token
    u_id = get_u_id(token)
    ch, i, deleted, valid = find_channel(message_id)
    if not valid or deleted:
        raise InputError(description="Message doesn't exist in channel")
    if u_id in db['channels'][ch]['owner_members']:
        if db['channels'][ch]['messages'][i]['is_pinned']:
            #message already pinned
            raise InputError(description='Message is already pinned')
        else:
            db['channels'][ch]['messages'][i]['is_pinned'] = True
    else:
        #user is not an owner
        raise AccessError(description='Cannot pin if you are not an owner')

    return {}

def message_unpin(token, message_id):
    '''unpins a message in channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError

    #get u_id and email from token
    u_id = get_u_id(token)
    ch, i, deleted, valid = find_channel(message_id)
    if not valid or deleted:
        raise InputError(description="Message doesn't exist in channel")
    if u_id in db['channels'][ch]['owner_members']:
        if db['channels'][ch]['messages'][i]['is_pinned']:
            db['channels'][ch]['messages'][i]['is_pinned'] = False
        else:
            #message already unpinned
            raise InputError(description='Message is already unpinned')
    else:
        #user is not an owner
        raise AccessError(description='Cannot unpin if you are not an owner')

    return {}