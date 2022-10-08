import atexit
import psycopg2


db = {
    'accounts': {

    },
    'channels': {

    }
}

con = None

def connect():
    global con
    try:
        con = psycopg2.connect(dbname="chat", user="user", password="pass")
        con.set_session(autocommit=True)
    except psycopg2.Error as err:
        print("DB error: ", err)

def get_db():
    if not (con):
        connect()
    return (con)

def exit_handler():
    if con:
        con.close()
        
atexit.register(exit_handler)

example_db = {
    'accounts': {
        'testemail@email.com': {
            'email': 'testemail@email.com',
            'password': 'abcde12345',
            'first_name': 'John',
            'last_name': 'Smith',
            'u_id': '5491838341617517521',
            'token': None, # Currently Logged Out
            'is_owner': True, # First User
        }
    },
    'channels': {
        '5491823341617512523': {
            'is_public': True,
            'channel_id': '5491823341617512523',
            'name': 'Test Channel',
            'owner_members': [
                '5491838341617517123',
            ],
            'all_members': [
                '5491838341617511245',
            ],
            'messages': [
                {
                    'message_id': '5491838341217511249',
                    'u_id': '5491838341617517521',
                    'message': 'test',
                    'time_created': 1601548644,
                    'reacts': [{
                        'react_id': 1,
                        'u_ids': [],
                        'is_this_user_reacted': False
                    }],
                    'is_pinned': 0
                }
            ],
            'deleted_messages': [
                'list of message ids'
            ]
        }
    }
}
