'''
Channels functions
'''
from db import get_db
from error import InputError
from helper_functions import get_u_id, token_validation

db = get_db()

def channels_list(token):
    '''
    Returns a dictionary of channels and details that the user is part of
    '''

    dict = {'channels': []}
    u_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute("select c.id, c.name from channels c, channel_users cu where cu.user_id = %s and c.id = cu.channel_id", [u_id])

        channels = cur.fetchall()

        for channel in channels:
            dict['channels'].append({
                'channel_id': channel[0],
                'name': channel[1]
            })
        
    return dict

def channels_listall(token):
    '''
    Returns a dictionary of all channels and their details
    '''

    channels = {'channels' : []}

    if not token_validation(token):
        return channels

    with db.cursor() as cur:
        cur.execute("select id, name from channels")

        for channel in cur.fetchall():
            channels['channels'].append({
                'channel_id': channel[0],
                'name': channel[1]
            })

    return channels

def channels_create(token, name, is_public):
    '''
    Returns channel_id if there is a newly created channel. Creates a new channel in db.
    Name cannot be longer than 20 characters
    User is automatically added to the owner and user lists
    '''

    is_public = is_public == 'True' or is_public

    user_id = get_u_id(token)

    if len(name) > 20:
        raise InputError

    with db.cursor() as cur:
        cur.execute(""" insert into channels (public, name)
                        values (%s, %s)
                        returning id""", [is_public, name])
        
        channel_id = cur.fetchone()[0]
        
        cur.execute("insert into channel_users (user_id, channel_id, admin) values (%s, %s, %s)", [user_id, channel_id, True])

        channel_dict = {'channel_id': channel_id}

    return channel_dict
