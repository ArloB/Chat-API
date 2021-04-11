'''
Channels functions
'''
from db import db
from error import InputError
from helper_functions import get_u_id, token_validation

def channels_list(token):
    '''
    Returns a dictionary of channels and details that the user is part of
    '''

    channels = {'channels': []}
    u_id = get_u_id(token)

    for num in db['channels']:
        if u_id in db['channels'][num]['all_members']:
           channels['channels'].append({'channel_id': db['channels'][num]['channel_id'], 'name':  db['channels'][num]['name']})

    return channels

def channels_listall(token):
    '''
    Returns a dictionary of all channels and their details
    '''

    channels = {'channels' : []}

    if not token_validation(token):
        return channels

    for num in db['channels']:
        channels['channels'].append({'channel_id': db['channels'][num]['channel_id'], 'name':  db['channels'][num]['name']})

    return channels

def channels_create(token, name, is_public):
    '''
    Returns channel_id if there is a newly created channel. Creates a new channel in db.
    Name cannot be longer than 20 characters
    User is automatically added to the owner and user lists
    '''

    is_public = is_public == 'True' or is_public

    if len(name) > 20:
        raise InputError

    channel_id = 0
    u_id = get_u_id(token)

    while channel_id in db['channels']:
        channel_id += 1

    db['channels'][channel_id] = {'name': name, 'channel_id': channel_id, \
    'is_public': is_public, 'owner_members': [u_id], 'all_members': [u_id], 'messages': []}

    channel_dict = {'channel_id': channel_id}

    return channel_dict
