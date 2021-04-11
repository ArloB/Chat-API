from channels import token_validation
from db import db
import os
import shutil
import pathlib
import glob
from error import *

def clear():
    db.clear()
    db['accounts'] = {}
    db['channels'] = {}

    img_path = os.path.join(pathlib.Path(__file__).parent, 'user_account_imgs')
    
    if os.path.exists(img_path):
        shutil.rmtree(img_path)

    return {}

def users_all(token):
    '''
    Returns all users in db and their associated details
    '''
    if not token_validation(token):
        return {'users': []}

    accounts = []

    for accs in db['accounts'].values():
        accounts.append(accs)

    return {'users': accounts}


def admin_userpermission_change(token, u_id, permission_id):
    '''
    Change the permissions of a user
    '''
    user_obj = None
    has_permission = False

    # Check if token is valid
    if not token_validation(token):
        raise InputError(description="Invalid token")

    for user in db['accounts'].values():
        if user.get('u_id') == u_id:
            user_obj = user
        if user.get('token') == token:
            # Prevent removing admin from self
            if user['is_owner']:
                has_permission = True

    # Check if calling user is owner
    if not has_permission:
        raise AccessError(description="User does not have permission to take this action")

    # Check if supplied u_id is a user
    if user_obj is None:
        raise InputError(description="Invalid u_id")

    # Set owner depending on permission_id, raise error if invalid
    if permission_id == 1:
        user_obj['is_owner'] = True
    elif permission_id == 2:
        user_obj['is_owner'] = False
    else:
        raise InputError(description="Invalid permission_id")

    return {}

def search(token, query_str):
    '''
    Return messages containing query_str substring
    '''
    channels = []
    u_id = None
    res = {
        'messages': []
    }

    # Get u_id for token
    for user in db['accounts'].values():
        if token == user['token']:
            u_id = user['u_id']

    # If token invalid return empty list
    if u_id is None:
        return res

    # Create list of channels user is in
    for channel in db['channels'].values():
        if u_id in channel['all_members']:
            channels.append(channel)

    # Go through all channels, matching messages containing substring and adding to res
    for channel in channels:
        if channel.get('messages', False):
            for message in channel.get('messages'):
                if query_str in message['message']:
                    res['messages'].append(message)
        
    return res

