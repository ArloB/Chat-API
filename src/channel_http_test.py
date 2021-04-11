'''
Channel HTTP Tests
'''
import requests


USER_DATA1 = {
    'email': 'haydensmith@gmail.com',
    'password': 'h4yd3nsm1th',
    'name_first': 'Hayden',
    'name_last': 'Smith'
}

USER_DATA2 = {
    'email': 'jaydensmith@gmail.com',
    'password': 'j4yd3nsm1th',
    'name_first': 'Jayden',
    'name_last': 'Smith'
}

def settingup(url):
    '''
    Helper function to create a database to test channel and message functions
    '''
    requests.delete(f"{url}/clear")
    url_register = url + 'auth/register'

    user1 = requests.post(url_register, json=USER_DATA1)
    u_1 = user1.json()
    user2 = requests.post(url_register, json=USER_DATA2)
    u_2 = user2.json()

    ch_data1 = {
        'token': u_1['token'],
        'name': 'The Smiths',
        'is_public': True
    }
    ch_data2 = {
        'token': u_2['token'],
        'name': 'Priv Smiths',
        'is_public': False
    }

    channel1 = requests.post(url + 'channels/create', json=ch_data1)
    c_1 = channel1.json()
    channel2 = requests.post(url + 'channels/create', json=ch_data2)
    c_2 = channel2.json()

    return u_1['u_id'], u_1['token'], u_2['u_id'], u_2['token'], \
        c_1['channel_id'], c_2['channel_id']

#channel_invite http tests

def test_invite_inputerror1(url):
    '''Input error when channel_id is empty'''
    _, token1, u_id2, _, _, _ = settingup(url)
    url_invite = url + 'channel/invite'
    data1 = {
        'token': token1,
        'channel_id': '',
        'u_id': u_id2
    }
    resp1 = requests.post(url_invite, json=data1)
    assert resp1.status_code == 400

def test_invite_inputerror2(url):
    '''Input error when channel_id doesn't exist'''
    _, token1, u_id2, _, _, _ = settingup(url)
    url_invite = url + 'channel/invite'
    data2 = {
        'token': token1,
        'channel_id': '231231313',
        'u_id': u_id2
    }
    resp2 = requests.post(url_invite, json=data2)
    assert resp2.status_code == 400

def test_invite_inputerror3(url):
    '''Input error when user_id is empty'''
    _, token1, _, _, valid_channel, _ = settingup(url)
    url_invite = url + 'channel/invite'
    data3 = {
        'token': token1,
        'channel_id': valid_channel,
        'u_id': ''
    }
    resp3 = requests.post(url_invite, json=data3)
    assert resp3.status_code == 400

def test_invite_inputerror4(url):
    '''Input error when user_id doesn't exist'''
    _, token1, _, _, valid_channel, _ = settingup(url)
    url_invite = url + 'channel/invite'
    data4 = {
        'token': token1,
        'channel_id': valid_channel,
        'u_id': 'invalid_id'
    }
    resp4 = requests.post(url_invite, json=data4)
    assert resp4.status_code == 400

def test_invite_accesserror1(url):
    '''Access error when token not part of channel'''
    _, token1, u_id2, _, _, priv_channel = settingup(url)
    url_invite = url + 'channel/invite'
    data1 = {
        'token': token1,
        'channel_id': priv_channel,
        'u_id': u_id2
    }
    resp1 = requests.post(url_invite, json=data1)
    assert resp1.status_code == 400

def test_invite_accesserror2(url):
    '''Access error when token invalid'''
    _, _, u_id2, _, _, priv_channel = settingup(url)
    url_invite = url + 'channel/invite'
    data2 = {
        'token': 'notvalid',
        'channel_id': priv_channel,
        'u_id': u_id2
    }
    resp2 = requests.post(url_invite, json=data2)
    assert resp2.status_code == 400

def test_invite_success(url):
    '''checks that user being invited was added to channel'''
    _, token1, u_id2, _, valid_channel, _ = settingup(url)
    url_invite = url + 'channel/invite'
    _ = url + 'channels/list'
    data1 = {
        'token': token1,
        'channel_id': valid_channel,
        'u_id': u_id2
    }
    r = requests.post(url_invite, json=data1)
    assert r.status_code == 200

def test_invite_self(url):
    '''checks a user can't invite themselves to a channel'''
    u_id1, token1, _, _, valid_channel, _ = settingup(url)
    url_invite = url + 'channel/invite'
    data = {
        'token': token1,
        'channel_id': valid_channel,
        'u_id': u_id1
    }
    r = requests.post(url_invite, json=data) #user_id inviting itself
    assert r.status_code == 200

def test_invite_failed(url):
    '''tests a person already in channel can't be reinvited'''
    _, token1, user2, token2, valid_channel, _ = settingup(url)
    url_join = url + 'channel/join'
    url_invite = url + 'channel/invite'
    data1 = {
        'token': token2,
        'channel_id': valid_channel
    }
    r = requests.post(url_join, json=data1)
    assert r.status_code == 200
    data2 = {
        'token': token1,
        'channel_id': valid_channel,
        'u_id': user2
    }
    r = requests.post(url_invite, json=data2)
    assert r.status_code == 200

#HTTP Tests for channel_details

def test_details_inputerror1(url):
    '''Input error when empty channel id'''
    _, _, token1, _, _, _ = settingup(url)
    url_details = url + 'channel/details'
    data1 = {
        'token': token1,
        'channel_id': ''
    }
    r = requests.get(url_details, params=data1)
    assert r.status_code == 400

def test_details_inputerror2(url):
    '''Input error when channel does not exist'''
    _, _, token1, _, _, _ = settingup(url)
    url_details = url + 'channel/details'
    data2 = {
        'token': token1,
        'channel_id': 123123
    }
    r = requests.get(url_details, params=data2)
    assert r.status_code == 400

def test_details_accesserror1(url):
    '''Access error when user not in channel'''
    url_details = url + 'channel/details'
    _, _, token1, _, _, channel_id2 = settingup(url)
    data1 = {
        'token': token1,
        'channel_id': channel_id2
    }
    r = requests.get(url_details, params=data1)
    assert r.status_code == 400

def test_details_accesserror2(url):
    '''Access error when token invalid'''
    url_details = url + 'channel/details'
    _, _, _, _, _, channel_id2 = settingup(url)
    data2 = {
        'token': 'notvalid',
        'channel_id': channel_id2
    }
    r = requests.get(url_details, params=data2)
    assert r.status_code == 400

def test_details_success(url):
    '''
    Testing that channel details returns correctly
    '''
    _, token1, _, _, ch_id1, _ = settingup(url)
    url_details = url + 'channel/details'
    data = {
        'token': token1,
        'channel_id': ch_id1
    }
    response = requests.get(url_details, params=data)
    assert response.status_code == 200

def test_details_success2(url): #test channel details with more than 1 member
    '''
    Testing channel details with more than one member
    '''
    _, token1, _, _, _, ch_id2 = settingup(url)
    url_details = url + 'channel/details'
    #user1 joins channel
    data = {
        'token': token1,
        'channel_id': ch_id2
    }
    r = requests.post(url + 'channel/join', json=data)
    assert r.status_code == 200
    #print details (user1 and user2 should be in owner members and all members)
    response = requests.get(url_details, params=data)
    assert response.status_code == 200

#Tests for channel_messages

def test_messages_inputerror1(url):
    '''Input error when empty channel id'''
    _, token1, _, _, _, _ = settingup(url)
    url_messages = url + 'channel/messages'
    data1 = {
        'token': token1,
        'channel_id': '',
        'start': '0'
    }
    r = requests.get(url_messages, params=data1)
    assert r.status_code == 400

def test_messages_inputerror2(url):
    '''Input error when channel does not exist'''
    _, token1, _, _, _, _ = settingup(url)
    url_messages = url + 'channel/messages'
    data2 = {
        'token': token1,
        'channel_id': '123123',
        'start': '0'
    }
    r = requests.get(url_messages, params=data2)
    assert r.status_code == 400

def test_messages_inputerror3(url):
    '''Input error when start > total msgs in channel'''
    _, _, _, token2, _, ch_id2 = settingup(url)
    url_messages = url + 'channel/messages'
    data3 = {
        'token': token2,
        'channel_id': ch_id2,
        'start': '100'
    }
    r = requests.get(url_messages, params=data3)
    assert r.status_code == 400

def test_messages_accesserror1(url):
    '''Access error when user not in channel'''
    _, token1, _, _, _, ch_id2 = settingup(url)
    url_messages = url + 'channel/messages'
    data1 = {
        'token': token1,
        'channel_id': ch_id2,
        'start': 0
    }
    r = requests.get(url_messages, params=data1)
    assert r.status_code == 400 #user not in channel
def test_messages_accesserror2(url):
    '''Access error when invalid token'''
    _, _, _, _, _, ch_id2 = settingup(url)
    url_messages = url + 'channel/messages'
    data2 = {
        'token': 'notvalid',
        'channel_id': ch_id2,
        'start': 0
    }
    r = requests.get(url_messages, params=data2)
    assert r.status_code == 400 #invalid token

def test_messages_empty(url):
    '''Testing a channel with no messages'''
    _, token1, _, _, ch_id1, _ = settingup(url)
    data = {
        'token': token1,
        'channel_id': ch_id1,
        'start': '0'
    }
    response = requests.get(url + 'channel/messages', params=data)
    assert response.status_code == 200

def test_messages_more(url):
    '''Sending more than 50 messages and only displaying 50'''
    _, _, u_id2, token2, _, ch_id2 = settingup(url)
    url_send = url + 'message/send'
    url_messages = url + 'channel/messages'
    messages = []
    data_send = {
        'token': token2,
        'channel_id': ch_id2,
        'message': 'c:'
    }
    for i in range(60):
        #get message_id from message_send
        response = requests.post(url_send, json=data_send)
        assert response.status_code == 200
        result = response.json()
        message_id = int(result['message_id'])
        #create a messages dictionary to test channel_messages against
        m_dict = {
            'message_id': message_id,
            'u_id': u_id2,
            'message': 'c:',
            'reacts': [],
            'is_pinned': False
        }
        if i < 50:
            messages.append(m_dict)
    messages.reverse()

    data_messages = {
        'token': token2,
        'channel_id': ch_id2,
        'start': 0
    }
    response = requests.get(url_messages, params=data_messages)
    assert response.status_code == 200

def test_messages_different_start(url):
    '''Checking channel_messages with start other than one'''
    _, _, u_id2, token2, _, ch_id2 = settingup(url)
    url_send = url + 'message/send'
    url_messages = url + 'channel/messages'
    messages = []
    data_send = {
        'token': token2,
        'channel_id': ch_id2,
        'message': 'c:',
    }
    for i in range(60):
        #get message_id from message_send
        response = requests.post(url_send, json=data_send)
        assert response.status_code == 200
        result = response.json()
        message_id = int(result['message_id'])
        #create a messages dictionary to test channel_messages against
        m_dict = {
            'message_id': message_id,
            'u_id': u_id2,
            'message': 'c:',
            'reacts': [],
            'is_pinned': False
        }
        if 1 <= i <= 50:
            messages.append(m_dict)
    messages.reverse()

    data_messages = {
        'token': token2,
        'channel_id': ch_id2,
        'start': 1
    }
    response = requests.get(url_messages, params=data_messages)
    assert response.status_code == 200

def test_messages_reach_end(url):
    '''Testing channel_messages when it reaches the end'''
    _, _, u_id2, token2, _, ch_id2 = settingup(url)
    url_send = url + 'message/send'
    url_messages = url + 'channel/messages'
    messages = []
    data_send = {
        'token': token2,
        'channel_id': ch_id2,
        'message': 'c:'
    }
    for i in range(20):
        #get message_id from message_send
        response = requests.post(url_send, json=data_send)
        assert response.status_code == 200
        result = response.json()
        message_id = int(result['message_id'])
        #create a messages dictionary to test channel_messages against
        m_dict = {
            'message_id': message_id,
            'u_id': u_id2,
            'message': 'c:',
            'reacts': [],
            'is_pinned': False
        }
        if i >= 10:
            messages.append(m_dict)
    messages.reverse()

    data_messages = {
        'token': token2,
        'channel_id': ch_id2,
        'start': 10
    }
    response = requests.get(url_messages, params=data_messages)
    assert response.status_code == 200

#channel_leave http tests

def test_leaveinputerror1(url):
    '''Input error when empty channel id'''
    _, token1, _, _, _, _ = settingup(url)
    url_leave = url + 'channel/leave'
    data1 = {
        'token': token1,
        'channel_id': ''
    }
    assert requests.post(url_leave, json=data1).status_code == 400

def test_leaveinputerror2(url):
    '''Input error when channel id doesn't exist'''
    _, token1, _, _, _, _ = settingup(url)
    url_leave = url + 'channel/leave'
    data2 = {
        'token': token1,
        'channel_id': 123
    }
    assert requests.post(url_leave, json=data2).status_code == 400

def test_leaveaccesserror1(url):
    '''Access error when token is not part of channel'''
    _, token1, _, _, _, priv_channel = settingup(url)
    url_leave = url + 'channel/leave'
    data1 = {
        'token': token1,
        'channel_id': priv_channel
    }
    assert requests.post(url_leave, json=data1).status_code == 400

def test_leaveaccesserror2(url):
    '''Access error when token is invalid'''
    _, _, _, _, _, priv_channel = settingup(url)
    url_leave = url + 'channel/leave'
    data2 = {
        'token': 'notvalid',
        'channel_id': priv_channel
    }
    assert requests.post(url_leave, json=data2).status_code == 400

def test_leavesuccess(url):
    '''checks that user does leave channel'''
    _, token1, u_id2, _, valid_channel, _ = settingup(url)
    url_leave = url + 'channel/leave'
    data1 = {
        'token': token1,
        'channel_id': valid_channel,
        'u_id': u_id2
    }
    r = requests.post(url + 'channel/invite', json=data1)
    assert r.status_code == 200
    r = requests.post(url_leave, json=data1)
    assert r.status_code == 200

#channel_join http tests
def test_join_inputerror1(url):
    '''Input error when empty channel id'''
    _, token1, _, _, _, _ = settingup(url)
    url_join = url + 'channel/join'
    data1 = {
        'token': token1,
        'channel_id': ''
    }
    r = requests.post(url_join, json=data1)
    assert r.status_code == 400

def test_join_inputerror2(url):
    '''Input error when channel id doesn't exist'''
    _, token1, _, _, _, _ = settingup(url)
    url_join = url + 'channel/join'
    data2 = {
        'token': token1,
        'channel_id': 123123
    }
    r = requests.post(url_join, json=data2)
    assert r.status_code == 400

def test_join_accesserror1(url):
    '''Access error when joining private channel'''
    _, _, _, _, _, priv_channel = settingup(url)
    url_join = url + 'channel/join'
    user_data = {
        'email': 'waydensmith@gmail.com',
        'password': 'w4yd3nsm1th',
        'name_first': 'Wayden',
        'name_last': 'Smith'
    }
    response = requests.post(url + 'auth/register', json=user_data)
    user = response.json()
    data1 = {
        'token': user['token'],
        'channel_id': priv_channel
    }
    r = requests.post(url_join, json=data1)
    assert r.status_code == 400

def test_join_accesserror2(url):
    '''Access error when invalid token'''
    _, _, _, _, _, priv_channel = settingup(url)
    url_join = url + 'channel/join'    
    data2 = {
        'token': 'notvalid',
        'channel_id': priv_channel
    }
    r = requests.post(url_join, json=data2)
    assert r.status_code == 400

def test_join_flockr_owner(url):
    '''successful if flockr owner joins priv channel'''
    _, token1, _, _, _, priv_channel = settingup(url)
    url_join = url + 'channel/join'
    data = {
        'token': token1,
        'channel_id': priv_channel
    }
    r = requests.post(url_join, json=data) #can join because owner of flockr
    assert r.status_code == 200

def test_join_success(url):
    '''successful when user joins public channel'''
    _, _, _, token2, valid_channel, _ = settingup(url)
    url_join = url + 'channel/join'
    data = {
        'token': token2,
        'channel_id': valid_channel
    }
    r = requests.post(url_join, json=data)
    assert r.status_code == 200

def test_joined_already(url):
    '''unsuccessful when user is already in channel'''
    _, token1, _, _, valid_channel, _ = settingup(url)
    url_join = url + 'channel/join'
    data = {
        'token': token1,
        'channel_id': valid_channel
    }
    response = requests.post(url_join, json=data) #user_id inviting itself
    assert response.status_code == 200

#Tests for channel_addowner

def test_addowner_ok(url):
    '''Test a valid addowner request'''
    requests.delete(f"{url}/clear")
    user1 = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    user2 = requests.post(f"{url}/auth/register", json={"email": "bb@b.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    channel_id = requests.post(f"{url}/channels/create", json={"token": user1['token'], "name": "channel", "is_public": True}).json()
    response = requests.post(f"{url}/channel/addowner", json={"token": user1['token'], "channel_id": channel_id['channel_id'], "u_id": user2['u_id']})
    assert response.status_code == 200

def test_addowner_invalid_channel_id(url):
    '''Test addowner with an invalid channel id'''
    requests.delete(f"{url}/clear")
    user1 = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    assert requests.post(f"{url}/channel/addowner", json={"token": user1['token'], "channel_id": 1234, "u_id": user1['u_id']}).status_code == 400

def test_addowner_user_already_owner(url):
    '''Test trying to add an owner as owner'''
    requests.delete(f"{url}/clear")
    user1 = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    channel_id = requests.post(f"{url}/channels/create", json={"token": user1['token'], "name": "channel", "is_public": True}).json()
    assert requests.post(f"{url}/channel/addowner", json={"token": user1['token'], "channel_id": channel_id['channel_id'], "u_id": user1['u_id']}).status_code == 400

def test_addowner_user_not_owner(url):
    '''Test adding an owner by a non owner account'''
    requests.delete(f"{url}/clear")
    user1 = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    user2 = requests.post(f"{url}/auth/register", json={"email": "bb@b.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    channel_id = requests.post(f"{url}/channels/create", json={"token": user1['token'], "name": "channel", "is_public": True}).json()
    assert requests.post(f"{url}/channel/addowner", json={"token": user2['token'], "channel_id": channel_id['channel_id'], "u_id": user2['u_id']}).status_code == 400

#Tests for channel_removeowner

def test_removeowner_self(url):
    '''Test remove self as owner'''
    requests.delete(f"{url}/clear")
    user1 = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    channel_id = requests.post(f"{url}/channels/create", json={"token": user1['token'], "name": "channel", "is_public": True}).json()
    assert requests.post(f"{url}/channel/removeowner", json={"token": user1['token'], "channel_id": channel_id['channel_id'], "u_id": user1['u_id']}).status_code == 200

def test_removeowner_other(url):
    '''Test removing another as owner'''
    requests.delete(f"{url}/clear")
    user1 = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    user2 = requests.post(f"{url}/auth/register", json={"email": "bb@b.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    channel_id = requests.post(f"{url}/channels/create", json={"token": user1['token'], "name": "channel", "is_public": True}).json()
    assert requests.post(f"{url}/channel/addowner", json={"token": user1['token'], "channel_id": channel_id['channel_id'], "u_id": user2['u_id']}).status_code == 200
    assert requests.post(f"{url}/channel/removeowner", json={"token": user1['token'], "channel_id": channel_id['channel_id'], "u_id": user2['u_id']}).status_code == 200

def test_removeowner_invalid_channel_id(url):
    '''Trying to remove an owner from an invalid channel'''
    requests.delete(f"{url}/clear")
    user1 = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    assert requests.post(f"{url}/channel/removeowner", json={"token": user1['token'], "channel_id": 1234, "u_id": user1['u_id']}).status_code == 400

def test_removeowner_user_not_owner(url):
    '''Trying to remove an owner when the user is not an owner'''
    requests.delete(f"{url}/clear")
    user1 = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    user2 = requests.post(f"{url}/auth/register", json={"email": "bb@b.com", "password": "123456", "name_first": "abc", "name_last": "def"}).json()
    channel_id = requests.post(f"{url}/channels/create", json={"token": user1['token'], "name": "channel", "is_public": True}).json()
    assert requests.post(f"{url}/channel/removeowner", json={"token": user2['token'], "channel_id": channel_id['channel_id'], "u_id": user1['u_id']}).status_code == 400
