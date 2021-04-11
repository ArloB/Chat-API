'''
Channel functions
'''
from error import InputError, AccessError
from helper_functions import get_u_id, token_validation
from db import db

def invite(token, channel_id, u_id):
    '''Inviting a user to a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')
    
    if channel_id != '':
        channel_id = int(channel_id)

    #check if channel id doesn't exist
    if channel_id not in db['channels']:
        raise InputError(description='Invalid Channel')

    #check if u_id doesn't exist
    check = 0
    for emails in db['accounts']:
        if db['accounts'][emails]['u_id'] == u_id:
            check = 1
    if check == 0:
        raise InputError(description='Invalid user')

    #checking token is not part of channel_id
    #first get u_id of the token
    user = get_u_id(token)

    #then check if token is in channel members
    if user not in db['channels'][channel_id]['all_members']:
        raise AccessError(description='User not part of channel')

    #check if u_id is a member of channel
    if u_id not in db['channels'][channel_id]['all_members']:
        #add u_id to list of members of channel_id
        db['channels'][channel_id]['all_members'].append(u_id)

    return {}

def details(token, channel_id):
    '''Provide details about a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    if channel_id != '':
        channel_id = int(channel_id)

    #if invalid channel id
    if channel_id not in db['channels']:
        raise InputError(description='Invalid Channel')

    #if token not in channel
    user_id = get_u_id(token) #get u_id of user
    if user_id not in db['channels'][channel_id]['all_members']: #check u_id not in channel
        raise AccessError(description='User not part of channel')

    owner_members, all_members = [], []

    for user in db['channels'][channel_id]['owner_members']:
        for account in db['accounts'].values():
            if account['u_id'] == user:
                owner_members.append({'u_id': user, 'name_first': \
                account['name_first'],'name_last': account['name_last'],
                'profile_img_url': account['profile_img_url']})

    for user in db['channels'][channel_id]['all_members']:
        for account in db['accounts'].values():
            if account['u_id'] == user:
                all_members.append({'u_id': user, 'name_first': \
                account['name_first'],'name_last': account['name_last'],
                'profile_img_url': account['profile_img_url']})

    #return a channel details dictionary with
    #the channel's details from the database
    return {
        'name':db['channels'][channel_id]['name'],
        'owner_members':owner_members,
        'all_members': all_members
    }

def create_msg_dict(start, stop, step, channel_id, user_id):
    messages_dict = {
        'messages': []
    }
    for i in range(start, stop, step):
            messages_list = db['channels'][channel_id]['messages'][i]
            #if user is part of reacts, make is_this_user_reacted = True
            if messages_list['reacts'] != []:
                if user_id in messages_list['reacts'][0]['u_ids']:
                    messages_list['reacts'][0]['is_this_user_reacted'] = True
                else:
                    messages_list['reacts'][0]['is_this_user_reacted'] = False
            messages_dict['messages'].append(messages_list)
    return messages_dict

def messages(token, channel_id, start):
    '''Provide a dictionary of up to 50 messages from a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    if channel_id != '':
        channel_id = int(channel_id)

    start = int(start)

    #if invalid channel id
    if channel_id not in db['channels']:
        raise InputError

    #if token not in channel
    user_id = get_u_id(token) #get u_id of user
    if user_id not in db['channels'][channel_id]['all_members']: #check u_id not in channel
        raise AccessError

    num_of_messages = len(db['channels'][channel_id]['messages'])
    #if start > total number of messages
    if start > num_of_messages:
        raise InputError
    #if empty, return empty dictionary
    if num_of_messages == 0:
        return {'messages': [], 'start': 0, 'end': -1}
    #create a dictionary with messages from stored data dictionary
    # from start to end
    if num_of_messages < 50 or start + 50 > num_of_messages:
        messages_dict = create_msg_dict(num_of_messages-1, start-1, -1, channel_id, user_id)
        messages_dict['end'] = -1
    # from start to start+50
    else:
        messages_dict = create_msg_dict(start+49, start-1, -1, channel_id, user_id)
        messages_dict['end'] = start+50
    messages_dict['start'] = start
    return messages_dict

def leave(token, channel_id):
    '''Remove a user from a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')
    
    if channel_id != '':
        channel_id = int(channel_id)

    #check channel_id doesn't exist
    if channel_id not in db['channels']:
        raise InputError(description='Invalid Channel')

    #checking token is part of channel_id
    #first get u_id of the token
    user = get_u_id(token)
    #then check if token is in channel members
    if user not in db['channels'][channel_id]['all_members']:
        raise AccessError(description='User not part of channel')

    #check if token is an owner and remove if they are
    if user in db['channels'][channel_id]['owner_members']:
        db['channels'][channel_id]['owner_members'].remove(user)

    #remove token as part of members of channel_id
    db['channels'][channel_id]['all_members'].remove(user)

    return {
    }

def join(token, channel_id):
    '''Add a user to a public channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    if channel_id != '':
        channel_id = int(channel_id)

    #check channel_id doesn't exist
    if channel_id not in db['channels']:
        raise InputError(description='Invalid Channel')

    user = 0
    email = ''

    #check token is already a member
    #first get u_id of the token
    for emails in db['accounts']:
        if db['accounts'][emails]['token'] == token:
            user = db['accounts'][emails]['u_id']
            email = db['accounts'][emails]['email']

    #check channel_id is private
    if not db['channels'][channel_id]['is_public']:
        if not db['accounts'][email]['is_owner']:
            raise AccessError(description='Cannot join private chanenl')

    #then check if token is in channel members
    if user in db['channels'][channel_id]['all_members']:
        pass
    #add token as part of members of channel_id
    else:
        if db['accounts'][email]['is_owner'] is True:
            db['channels'][channel_id]['owner_members'].append(user)
        db['channels'][channel_id]['all_members'].append(user)

    return {
    }

def addowner(token, channel_id, u_id):
    '''Make a user an owner of a channel'''
    if not channel_id == '':
        channel_id = int(channel_id)

    # Check if channel_id exists
    if not db.get('channels', False) or channel_id not in db['channels']:
        raise InputError

    # Check if user is already channel owner
    if u_id in db['channels'][channel_id]['owner_members']:
        raise InputError

    for email in db['accounts']:
        channel_owner = db['accounts'][email]['u_id'] in db['channels']\
        [channel_id]['owner_members']

        if token == db['accounts'][email]['token']:
            # Check if user is an owner (server or channel)
            if db['accounts'][email]['is_owner'] or channel_owner:
                db['channels'][channel_id]['owner_members'].append(u_id)
                if u_id not in db['channels'][channel_id]['all_members']:
                    db['channels'][channel_id]['all_members'].append(u_id)
            else:
                raise AccessError
    
    return {}

def removeowner(token, channel_id, u_id):
    '''Remove an owner of a channel to just a member'''
    if not channel_id == '':
        channel_id = int(channel_id)

    # Check if channel_id exists
    if not db.get('channels', False) or channel_id not in db['channels']:
        raise InputError

    # Check if user is not channel owner
    if u_id not in db['channels'][channel_id]['owner_members']:
        raise InputError

    for email in db['accounts']:
        curr_uid = db['accounts'][email]['u_id']

        is_channel_owner = curr_uid in db['channels']\
        [channel_id]['owner_members']

        if token in db['accounts'][email]['token']:
            if db['accounts'][email]['is_owner'] or is_channel_owner:
                db['channels'][channel_id]['owner_members'].remove(u_id)
            else:
                raise AccessError
            
    return {}