from db import db

def get_u_id(token):
    '''
    Helper function that retrieves u_id of the associated token
    '''
    for email in db['accounts']:
        if token == db['accounts'][email]['token']:
            return db['accounts'][email]['u_id']

def token_validation(token):
    '''
    Helper function that checks if the token is valid
    '''
    for email in db['accounts']:
        if token == db['accounts'][email]['token']:
            return True
    return False

