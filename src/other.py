from helper_functions import msg_dict_helper, token_validation
from db import get_db
import os
import shutil
import pathlib
from error import *
from helper_functions import get_u_id

db = get_db()

def clear():
    with db.cursor() as cur:
        cur.execute("truncate channels, users, channel_users, messages, reacts")
        
        cur.execute("alter sequence channels_id_seq restart")
        cur.execute("alter sequence messages_id_seq restart")
        cur.execute("alter sequence users_id_seq restart")

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

    with db.cursor() as cur:
        cur.execute("select * from users")
        
        for user in cur.fetchall():
            accounts.append({
                "u_id": user[0],
                'email': user[1],
                'name_first': user[3],
                'name_last': user[4],
                'handle_str': user[5],
                'profile_img_url': user[6]
            })

    return {'users': accounts}


def admin_userpermission_change(token, u_id, permission_id):
    '''
    Change the permissions of a user
    '''
    if not token_validation(token):
        raise InputError(description="Invalid token")
    
    user_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute("select owner from users where id = %s", [user_id])
        
        if not bool(cur.fetchone()[0]):
            raise AccessError(description="User does not have permission to take this action")
        
        if int(user_id) == int(u_id):
            raise InputError(description="User cannot remove admin from self")
        
        cur.execute("select owner from users where id = %s", [u_id])
        
        if cur.rowcount == 0:
            raise InputError(description="Invalid u_id")
        
        is_owner = cur.fetchone()[0]
        
        if permission_id == 1:
            if not is_owner:
                cur.execute("update users set owner = true where id = %s", [u_id])
        elif permission_id == 2:
            if is_owner:
                cur.execute("update users set owner = false where id = %s", [u_id])
        else:
            raise InputError(description="Invalid permission_id")

    return {}

def search(token, query_str):
    '''
    Return messages containing query_str substring
    '''
    if not token_validation(token):
        raise InputError(description="Invalid token")
    
    user_id = get_u_id(token)
    
    res = {
        'messages': []
    }
    
    with db.cursor() as cur:
        cur.execute(""" select m.*, r.* 
                        from messages m
                        left join channel_users cu on cu.channel_id = m.channel_id
                        left join reacts r on r.message_id = m.id
                        where cu.user_id = %s and m.message ~* %s""", [user_id, query_str])
        
        res = msg_dict_helper(cur.fetchall())
        
    return res

