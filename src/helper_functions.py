import jwt
from db import get_db

db = get_db()

def decode_token(token):
    '''
    Extracts u_id and login time
    '''
    vals = jwt.decode(token, 'secret', algorithms=['HS512'])
    return [int(vals["u_id"]), int(vals["iat"])]

def get_u_id(token):
    '''
    Helper function that retrieves u_id of the associated token
    '''
    u_id, _ = decode_token(token)
    
    return u_id

def token_validation(token):
    '''
    Helper function that checks if the token is valid
    '''
    try:
        u_id, iat = decode_token(token)
    except:
        return False
        
    try:
        with db.cursor() as cur:
            cur.execute("select iat from users where id = %s", [u_id])
            
            return int(iat) == int(cur.fetchone()[0])
    except:
        return False

def msg_dict_helper(msgs):
    messages_dict = {
        'messages': []
    }
    
    messages = {}
    reacts = {}
    
    for msg in msgs:
        if msg[8] is not None:
            react = reacts.get(msg[0])
            
            if react is None:
                reacts[msg[0]] = {}
            
            curr = reacts[msg[0]].get(msg[8])
    
            if curr is None:
                reacts[msg[0]][msg[8]] = {
                    'react_id': msg[8],
                    'u_ids': [msg[6]],
                    'is_this_user_reacted': msg[2] == msg[6]
                }
            else:
                if not msg[2] in curr["u_ids"]:
                    curr["u_ids"].add(msg[2])
                
                if not curr["is_this_user_reacted"]:
                    curr["is_this_user_reacted"] = msg[2] == msg[6]
                
        messages[msg[0]] = {
            'message_id': msg[0],
            'u_id': msg[2],
            'message': msg[3],
            'time_created': msg[4],
            'reacts': [],
            'is_pinned': msg[5]
        }
                
    for m in sorted(messages.keys(), reverse=True):
        if reacts.get(m) is not None:
            for r in reacts[m]:
                messages[m]["reacts"].append(reacts[m][r])
        else:
            messages[m]["reacts"] = []
        
        messages_dict["messages"].append(messages[m])
        
    return messages_dict