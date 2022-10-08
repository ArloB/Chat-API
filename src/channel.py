'''
Channel functions
'''
from error import InputError, AccessError
from helper_functions import get_u_id, msg_dict_helper, token_validation
from db import get_db

db = get_db()

def invite(token, channel_id, u_id):
    '''Inviting a user to a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')
    
    if channel_id:
        channel_id = int(channel_id)
        
    user_id = get_u_id(token)
        
    with db.cursor() as cur:
        cur.execute("select * from channels where id = %s", [channel_id])
        
        if not cur.rowcount:
            raise InputError(description='Invalid Channel')
        
        cur.execute("select * from users where id = %s", [u_id])
        
        if not cur.rowcount:
            raise InputError(description='Invalid user')
        
        cur.execute(""" select u.id 
                        from users u, channel_users cu 
                        where u.id in (%s, %s) and cu.user_id = u.id and cu.channel_id = %s""", [user_id, u_id, channel_id])
        
        users = cur.fetchall()
        
        if len(users) == 1:
            if int(users[0][0]) == int(user_id):
                cur.execute("insert into channel_users (user_id, channel_id) values (%s, %s)", [u_id, channel_id])
            else:
                raise AccessError(description='User not part of channel')
        elif len(users) == 0:
            raise AccessError(description='User not part of channel')

    return {}

def details(token, channel_id):
    '''Provide details about a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    if channel_id:
        channel_id = int(channel_id)

    user_id = get_u_id(token)
    
    owner_members, all_members = [], []
    
    name = None
    
    with db.cursor() as cur:
        cur.execute("select * from channels where id = %s", [channel_id])
        
        if not cur.rowcount:
            raise InputError(description='Invalid Channel')
        
        cur.execute("select * from channel_users where user_id = %s and channel_id = %s", [user_id, channel_id])
                    
        if cur.rowcount == 0:
            raise AccessError(description='User not part of channel')
        
        cur.execute("select name from channels where id = %s", [channel_id])
        
        name = cur.fetchone()[0]
        
        cur.execute(""" select cu.admin, u.*
                        from users u, channel_users cu
                        where cu.user_id = u.id and cu.channel_id = %s
                        """, [channel_id])
        
        for user in cur.fetchall():
            if user[0]:
                owner_members.append({'u_id': user[1], 'name_first': user[4],'name_last': user[5], 'profile_img_url': user[7]})

            all_members.append({'u_id': user[1], 'name_first': user[4],'name_last': user[5], 'profile_img_url': user[7]})

    #return a channel details dictionary with
    #the channel's details from the database
    return {
        'name': name,
        'owner_members': owner_members,
        'all_members': all_members
    }

def create_msg_dict(start, stop, channel_id, user_id):
    messages_dict = {
        'messages': []
    }
    
    with db.cursor() as cur:
        cur.execute(""" select m.*, r.* from messages m
                        left join channel_users cu on cu.user_id = %s
                        left join reacts r on r.message_id = m.id
                        where m.channel_id = %s and cu.channel_id = m.channel_id
                        offset %s limit %s
                    """, [user_id, channel_id, start, stop - start])
        
        messages_dict = msg_dict_helper(cur.fetchall())
            
    return messages_dict

def messages(token, channel_id, start):
    '''Provide a dictionary of up to 50 messages from a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    if channel_id:
        channel_id = int(channel_id)

    start = int(start)
    
    user_id = get_u_id(token)

    with db.cursor() as cur:
        cur.execute("select * from channels where id = %s", [channel_id])
        
        if not cur.rowcount:
            raise InputError(description='Invalid Channel')
        
        cur.execute("select * from channel_users where user_id = %s and channel_id = %s", [user_id, channel_id])
                    
        if cur.rowcount == 0:
            raise AccessError(description='User not part of channel')

        cur.execute("select count(id) from messages where channel_id = %s", [channel_id])
        
        rows = int(cur.fetchone()[0])
        
        if start > rows:
            raise InputError("Invalid starting position")
        
        if rows == 0:
            return {'messages': [], 'start': 0, 'end': -1}
        
        if rows < 50 or start + 50 > rows:
            messages_dict = create_msg_dict(start, rows, channel_id, user_id)
            messages_dict['end'] = -1
        else:
            messages_dict = create_msg_dict(start, start + 50, channel_id, user_id)
            messages_dict['end'] = start + 50
        
        messages_dict['start'] = start
    
    return messages_dict

def leave(token, channel_id):
    '''Remove a user from a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')
    
    if channel_id:
        channel_id = int(channel_id)

    user_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute("select * from channels where id = %s", [channel_id])
        
        if not cur.rowcount:
            raise InputError(description='Invalid Channel')
        
        cur.execute("select * from channel_users where user_id = %s and channel_id = %s", [user_id, channel_id])
                    
        if cur.rowcount == 0:
            raise AccessError(description='User not part of channel')
        
        cur.execute("delete from channel_users where user_id = %s and channel_id = %s", [user_id, channel_id])

    return {}

def join(token, channel_id):
    '''Add a user to a public channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    if channel_id:
        channel_id = int(channel_id)

    user_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute("select * from channels where id = %s", [channel_id])
        
        if not cur.rowcount:
            raise InputError(description='Invalid Channel')
        
        cur.execute("select * from channel_users where user_id = %s and channel_id = %s", [user_id, channel_id])
                    
        if cur.rowcount != 0:
            return {}                
        
        cur.execute("select public from channels where id = %s", [channel_id])
        
        if not bool(cur.fetchone()[0]):
            raise AccessError(description='Cannot join private chanenl')
        
        cur.execute("insert into channel_users (channel_id, user_id) values (%s, %s)", [channel_id, user_id])
        
        cur.execute("select owner from users where id = %s", [user_id])
        
        if bool(cur.fetchone()[0]):
            cur.execute("update channel_users set admin = true where channel_id = %s and user_id = %s", [channel_id, user_id])
            
    return {}

def addowner(token, channel_id, u_id):
    '''Make a user an owner of a channel'''
    if not channel_id == '':
        channel_id = int(channel_id)

    user_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute("select * from channels where id = %s", [channel_id])
        
        if not cur.rowcount:
            raise InputError(description='Invalid Channel')
        
        cur.execute("select admin from channel_users where channel_id = %s and user_id = %s", [channel_id, u_id])
        
        status = cur.fetchone()
        
        if status == None:
            cur.execute("insert into channel_users (channel_id, user_id, admin) values (%s, %s, true)", [channel_id, u_id])
            return {}
        
        if bool(status[0]):
            raise InputError("Already an owner")
        
        cur.execute("select cu.admin, u.owner from channel_users cu left join users u on cu.id = u.user_id where cu.channel_id = %s and cu.user_id = %s", [channel_id, user_id])
        
        vals = cur.fetchall()
        
        if bool(vals[0][0]) or bool(vals[0][1]):
            cur.execute("update channel_users set admin = true where channel_id = %s and user_id = %s", [channel_id, u_id])
        else:
            raise AccessError
            
    return {}

def removeowner(token, channel_id, u_id):
    '''Remove an owner of a channel to just a member'''
    if not channel_id == '':
        channel_id = int(channel_id)

    user_id = get_u_id(token)

    with db.cursor() as cur:
        cur.execute("select * from channels where id = %s", [channel_id])
        
        if not cur.rowcount:
            raise InputError(description='Invalid Channel')
        
        cur.execute("select admin from channel_users where channel_id = %s and user_id = %s", [channel_id, u_id])
        
        status = cur.fetchone()
        
        if status == None or not bool(status[0]):
            raise InputError("Not an owner")
        
        cur.execute("select cu.admin, u.owner from channel_users cu left join users u on cu.id = u.user_id where cu.channel_id = %s and cu.user_id = %s", [channel_id, user_id])
        
        vals = cur.fetchall()
        
        if bool(vals[0][0]) or bool(vals[0][1]):
            cur.execute("update channel_users set admin = false where channel_id = %s and user_id = %s", [channel_id, u_id])
        else:
            raise AccessError
            
    return {}