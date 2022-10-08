'''Message functions'''
from datetime import datetime
import threading

from error import InputError, AccessError
from channels import get_u_id, token_validation
from db import get_db

db = get_db()

def message_send(token, channel_id, message):
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    if len(message) > 1000:
        raise InputError(description='Message too long')

    u_id = get_u_id(token)
    
    id = -1
    
    with db.cursor() as cur:
        cur.execute("select * from channels where id = %s", [channel_id])
        
        if not cur.rowcount:
            raise InputError(description='Invalid Channel')
        
        cur.execute(""" select u.id
                        from users u, channel_users cu 
                        where u.id = %s and cu.user_id = u.id and cu.channel_id = %s""", [u_id, channel_id])
                    
        if cur.rowcount == 0:
            raise AccessError(description='User not part of channel')

        cur.execute('insert into messages (channel_id, user_id, message, time) values (%s, %s, %s, %s) returning id', [channel_id, u_id, message, int(datetime.now().timestamp())])

        id = cur.fetchone()[0]

    return {
        'message_id': id,
    }

def message_remove(token, message_id):
    '''removing a message from a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    u_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute("""select cu.admin, m.user_id from messages m, channels c, channel_users cu
                        where c.id = m.channel_id and m.id = %s and cu.channel_id = c.id
                        and cu.user_id = %s""", [message_id, u_id])
         
        admin = cur.fetchone()
        
        if admin is None:
            raise AccessError(description="Message doesn't exist")
        elif not bool(admin[0]) or int(admin[1]) != int(u_id):
            raise AccessError(description="User does not have permission")
        
        cur.execute("delete from messages where id = %s", [message_id])
        cur.execute("delete from reacts where message_id = %s", [message_id])
        
    return {}

def message_edit(token, message_id, message):
    '''editing a message in a channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError(description='Invalid Token')

    #get u_id and email from token
    u_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute("""select cu.admin, m.user_id from messages m, channels c, channel_users cu
                        where c.id = m.channel_id and m.id = %s and cu.channel_id = c.id
                        and cu.user_id = %s""", [message_id, u_id])
         
        admin = cur.fetchone()
        
        if admin is None:
            raise AccessError(description="Message doesn't exist")
        elif not bool(admin[0]) or int(admin[1]) != int(u_id):
            raise AccessError(description="User does not have permission")
        
        cur.execute("update messages set message = %s where id = %s", [message, message_id])
        
    return {}

def message_sendlater(token, channel_id, message, time_sent):
    '''sends message to channel at later time'''
    if time_sent < int(datetime.now().timestamp()):
        raise InputError(description='Cannot send message to past')
    
    threading.Timer(time_sent-int(datetime.now().timestamp()), message_send, args=[token, channel_id, message]).start()

    return {}

def message_react(token, message_id, react_id = 1):
    '''Reacting to a message in a channel'''
    if not token_validation(token): #check valid token
        raise AccessError(description='Invalid Token')
    
    u_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute(""" select cu.* from messages m, channels c, channel_users cu
                        where m.id = %s and m.channel_id = c.id and cu.channeL_id = c.id and cu.user_id = %s""", [message_id, u_id])
        
        if cur.rowcount == 0:
            raise InputError(description="Unable to access message")
        
        cur.execute("select * from reacts where user_id = %s and message_id = %s and type = %s", [u_id, message_id, react_id])
        
        if cur.rowcount > 0:
            raise InputError(description="Already reacted to message")
        
        cur.execute("insert into reacts (user_id, message_id, type) values (%s, %s, %s)", [u_id, message_id, react_id])
        
    return {}

def message_unreact(token, message_id, react_id):
    #check valid token
    if not token_validation(token):
        raise AccessError(description='Invalid Token')
    
    u_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute(""" select cu.* from messages m, channels c, channel_users cu
                        where m.id = %s and m.channel_id = c.id and cu.channeL_id = c.id and cu.user_id = %s""", [message_id, u_id])
        
        if cur.rowcount == 0:
            raise InputError(description="Unable to access message")
        
        cur.execute("select * from reacts where user_id = %s and message_id = %s and type = %s", [u_id, message_id, react_id])
        
        if cur.rowcount == 0:
            raise InputError(description="Could not find react")
        
        cur.execute("delete from reacts where user_id = %s and message_id = %s and type = %s", [u_id, message_id, react_id])
            
    return {}

def message_pin(token, message_id):
    '''pins a message in channel'''
    if not token_validation(token):
        raise AccessError

    u_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute(""" select cu.* from messages m, channels c, channel_users cu
                        where m.id = %s and m.channel_id = c.id and cu.channeL_id = c.id and cu.user_id = %s""", [message_id, u_id])
        
        if cur.rowcount == 0:
            raise InputError(description="Unable to access message")
        
        cur.execute(""" select m.pinned, cu.admin from messages m, channel_users cu
                        where m.id = %s and cu.channel_id = m.channel_id and cu.user_id = %s""", [message_id, u_id])
        
        if cur.rowcount == 0:
            raise InputError(description="Message doesn't exist in channel")    

        vals = cur.fetchone()
        
        if bool(vals[0]):
            raise InputError(description='Message is already pinned')
        
        if not bool(vals[1]):
            raise AccessError(description='Cannot pin if you are not an owner')
        
        cur.execute("update messages set pinned = true where id = %s", [message_id])

    return {}

def message_unpin(token, message_id):
    '''unpins a message in channel'''
    #check if token is valid
    if not token_validation(token):
        raise AccessError

    u_id = get_u_id(token)
    
    with db.cursor() as cur:
        cur.execute(""" select cu.* from messages m, channels c, channel_users cu
                        where m.id = %s and m.channel_id = c.id and cu.channeL_id = c.id and cu.user_id = %s""", [message_id, u_id])
        
        if cur.rowcount == 0:
            raise InputError(description="Unable to access message")
        
        cur.execute(""" select m.pinned, cu.admin from messages m, channel_users cu
                        where m.id = %s and cu.channel_id = m.channel_id and cu.user_id = %s""", [message_id, u_id])
        
        if cur.rowcount == 0:
            raise InputError(description="Message doesn't exist in channel")    

        vals = cur.fetchone()
        
        if not bool(vals[0]):
            raise InputError(description='Message is not pinned')
        
        if not bool(vals[1]):
            raise AccessError(description='Cannot unpin if you are not an owner')
        
        cur.execute("update messages set pinned = false where id = %s", [message_id])

    return {}