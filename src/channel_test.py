import pytest
from error import InputError, AccessError
from other import clear

from channel import * #import all functions being tested

from auth import auth_register
from channels import channels_create, channels_list
from message import message_send
from time import time

'''
Create backend for functions: invite, join, leave
'''
def create_backend():
    clear()
    user1 = auth_register('haydensmith@gmail.com', 'h4yd3nsm1th', 'Hayden', 'Smith')
    u_id1 = user1['u_id']
    token1 = user1['token']
    user2 = auth_register('jaydensmith@gmail.com', 'j4yd3nsm1th', 'Jayden', 'Smith')
    u_id2 = user2['u_id']
    token2 = user2['token']

    valid_channel = channels_create(token1, 'The Smiths', True)
    valid_channel_id = valid_channel['channel_id']
    priv_channel = channels_create(token2, 'Priv Smiths', False)
    priv_channel_id = priv_channel['channel_id']

    return u_id1, token1, u_id2, token2, valid_channel_id, priv_channel_id

'''
Setup functions for details, messages
'''
def setup():
    clear()
    #create a user token
    user1 = auth_register("em1@email.com", "passwd1", "f_name1", "l_name1")
    u_id1 = user1['u_id']
    token1 = user1['token']
    user2 = auth_register("em2@email.com", "passwd2", "f_name2", "l_name2")
    u_id2 = user2['u_id']
    token2 = user2['token']

    #create a channel
    valid_channel1 = channels_create(token1, "Channel 1", True)
    valid_channel_id1 = valid_channel1['channel_id']
    valid_channel2 = channels_create(token2, "Channel 2", True)
    valid_channel_id2 = valid_channel2['channel_id'] 

    return u_id1, u_id2, token1, token2, valid_channel_id1, valid_channel_id2

'''
Tests for invite
'''
def test_invite_empty_chid():
    '''input error when channel id is empty'''
    _, token1, u_id2, _, _, _ = create_backend()
    with pytest.raises(InputError):
        invite(token1, '', u_id2)

def test_invite_invalid_chid():
    '''input error when channel id doesn't exist'''
    _, token1, u_id2, _, _, _ = create_backend()
    with pytest.raises(InputError):
        invite(token1, 10, u_id2)

def test_invite_empty_uid():
    '''input error when user id is empty'''
    _, token1, _, _, valid_channel, _ = create_backend()
    with pytest.raises(InputError):
        invite(token1, valid_channel, '')

def test_invite_invalid_uid():
    '''input error when user id doesn't exist'''
    _, token1, _, _, valid_channel, _ = create_backend()
    with pytest.raises(InputError):
        invite(token1, valid_channel, 'invalid_id')

def test_invite_accesserror():
    '''access error when token is not part of channel'''
    _, token1, u_id2, _, _, priv_channel = create_backend()
    with pytest.raises(AccessError):
        invite(token1, priv_channel, u_id2)

def test_invite_invalid_token():
    '''access error when token is invalid'''
    _, _, u_id2, _, _, priv_channel = create_backend()
    with pytest.raises(AccessError):
        invite('invalid_token', priv_channel, u_id2)

def test_invite_success():
    '''user 1 successfully inviting user2'''
    _, token1, u_id2, token2, valid_channel, _ = create_backend()
    invite(token1, valid_channel, u_id2)
    u_id2_channels = channels_list(token2)
    if valid_channel != u_id2_channels['channels'][0]['channel_id']:
        raise Exception("Failed")

def test_invite_self():
    '''trying to reinvite themself'''
    u_id1, token1, _, _, valid_channel, _ = create_backend()
    u_id1_channels = channels_list(token1)
    u_id1_channels_num_before = len(u_id1_channels['channels'])
    invite(token1, valid_channel, u_id1) #user_id inviting itself
    u_id1_channels_num_after = len(u_id1_channels['channels'])
    if u_id1_channels_num_before != u_id1_channels_num_after:
        raise Exception("Failed")

def test_invite_failed():
    _, token1, user2, token2, valid_channel, _ = create_backend()
    join(token2, valid_channel)
    u_id2_channels = channels_list(token2)
    u_id2_channels_num_before = len(u_id2_channels['channels'])
    invite(token1, valid_channel, user2)
    u_id2_channels_num_after = len(u_id2_channels['channels'])
    if u_id2_channels_num_before != u_id2_channels_num_after:
        raise Exception("Failed")
    
'''
Tests for details
'''
def test_details_empty_chid():
    '''input error when channel id is empty'''
    _, _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        details(token1, '')

def test_details_invalid_chid():
    '''input error when channel id doesn't exist'''
    _, _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        details(token1, 100)
        
def test_details_accesserror():
    '''access error when token is not part of channel'''
    _, _, token1, _, _, valid_channel_id2 = setup()
    with pytest.raises(AccessError):
        details(token1, valid_channel_id2)

def test_details_invalid_token():
    '''access error when token is invalid'''
    _, _, _, _, _, valid_channel_id2 = setup()
    with pytest.raises(AccessError):
        details('invalid_token', valid_channel_id2)

def test_details_success():
    '''getting the right details from a channel'''
    u_id1, _, token1, _, valid_channel_id1, _ = setup()
    result = details(token1, valid_channel_id1)
    assert result == {
        'name': 'Channel 1',
        'owner_members': [
            {'u_id': u_id1, 'name_first': 'f_name1', 'name_last': 'l_name1', 'profile_img_url': None}
        ],
        'all_members': [
            {'u_id': u_id1, 'name_first': 'f_name1', 'name_last': 'l_name1', 'profile_img_url': None}
        ]
    }
def test_details_success2():
    '''geting the right details from a channel with more than one member'''
    u_id1, u_id2, token1, token2, _, valid_channel_id2 = setup()
    addowner(token2, valid_channel_id2, u_id1)
    result = details(token1, valid_channel_id2)
    assert result == {
        'name': 'Channel 2',
        'owner_members': [{'u_id': u_id2, 'name_first': 'f_name2', 'name_last': 'l_name2', 'profile_img_url': None}, 
        {'u_id': u_id1, 'name_first': 'f_name1', 'name_last': 'l_name1', 'profile_img_url': None}],
        'all_members': [{'u_id': u_id2, 'name_first': 'f_name2', 'name_last': 'l_name2', 'profile_img_url': None}, 
        {'u_id': u_id1, 'name_first': 'f_name1', 'name_last': 'l_name1', 'profile_img_url': None}]
    }

'''
Tests for messages
'''
def test_messages_empty_chid():
    '''input error when channel id is empty'''
    _, _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        messages(token1, '', 0)

def test_messages_invalid_chid():
    '''input error when channel does not exist'''
    _, _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        messages(token1, 100, 0)

def test_messages_start():
    '''input error when start is greater than total number of messages'''
    _, _, _, token2, _, valid_channel_id2 = setup()
    with pytest.raises(InputError):
        messages(token2, valid_channel_id2, 100)

def test_messages_accesserror():
    '''access error when user is not part of channel'''
    _, _, token1, _, _, valid_channel_id2 = setup()
    with pytest.raises(AccessError):
        messages(token1, valid_channel_id2, 0)

def test_messages_invalid_token():
    '''access error when token is invalid'''
    _, _, _, _, _, valid_channel_id2 = setup()
    with pytest.raises(AccessError):
        messages('invalid_token', valid_channel_id2, 0)

def test_messages_empty():
    '''testing when channel has no messages'''
    _, _, token1, _, valid_channel_id1, _ = setup()
    result = messages(token1, valid_channel_id1, 0)
    assert result == {
        'messages': [
        ],
        'start': 0,
        'end': -1,
    }

def test_messages_more():
    '''Sending more than 50 messages and only displaying 50'''
    _, u_id2, _, token2, _, ch_id2 = setup()
    msg = []
    for i in range(60):
        message_id = message_send(token2, ch_id2, 'c:')
        m_id = message_id['message_id']
        #create a messages dictionary to test channel_messages against
        m_dict = {
            'message_id': m_id,
            'u_id': u_id2,
            'message': 'c:',
            'time_created': int(time()),
            'reacts': [],
            'is_pinned': False
        }
        if i < 50:
            msg.append(m_dict)
    msg.reverse()
    result = messages(token2, ch_id2, 0)
    assert result == {
        'messages' : msg,
        'start': 0,
        'end': 50
    }




def test_messages_different_start():
    '''Checking channel_messages with start other than one'''
    _, u_id2, _, token2, _, ch_id2 = setup()
    msg = []
    for i in range(60):
        message_id = message_send(token2, ch_id2, 'c:')
        m_id = message_id['message_id']
        #create a messages dictionary to test channel_messages against
        m_dict = {
            'message_id': m_id,
            'u_id': u_id2,
            'message': 'c:',
            'time_created': int(time()),
            'reacts': [],
            'is_pinned': False
        }
        if 1 <= i <= 50:
            msg.append(m_dict)
    msg.reverse()
    result = messages(token2, ch_id2, 1)
    assert result == {
        'messages': msg,
        'start': 1,
        'end': 51
    }

def test_messages_reach_end():
    '''Testing channel_messages when it reaches the end'''
    _, u_id2, _, token2, _, ch_id2 = setup()
    msg = []
    for i in range(20):
        message_id = message_send(token2, ch_id2, 'c:')
        m_id = message_id['message_id']
        #create a messages dictionary to test channel_messages against
        m_dict = {
            'message_id': m_id,
            'u_id': u_id2,
            'message': 'c:',
            'time_created': int(time()),
            'reacts': [],
            'is_pinned': False
        }
        if i >= 10:
            msg.append(m_dict)
    msg.reverse()
    result = messages(token2, ch_id2, 10)
    assert result == {
        'messages': msg,
        'start': 10,
        'end': -1
    }

'''
Tests for leave
'''
def test_leave_empty_chid():
    '''input error when channel id is empty'''
    _, token1, _, _, _, _ = create_backend()
    with pytest.raises(InputError):
        leave(token1, '')

def test_leave_invalid_chid():
    '''input error when channel id doesn't exist'''
    _, token1, _, _, _, _ = create_backend()
    with pytest.raises(InputError):
        leave(token1, 100)

def test_leave_accesserror():
    '''access error when token is not part of channel'''
    _, token1, _, _, _, priv_channel = create_backend()
    with pytest.raises(AccessError):
        leave(token1, priv_channel)

def test_leave_invalid_token():
    '''access error when token is invalid'''
    _, _, _, _, _, priv_channel = create_backend()
    with pytest.raises(AccessError):
        leave('invalid_token', priv_channel)

def test_leave_success():
    _, token1, _, _, valid_channel, _ = create_backend()
    leave(token1, valid_channel) 
    u_id1_channels = channels_list(token1)
    if valid_channel in u_id1_channels['channels']:
        raise Exception("Failed")

'''
Tests for join
'''

def test_join_inputerror():
    '''input error when channel_id is empty'''
    _, token1, _, _, _, _ = create_backend()
    with pytest.raises(InputError):
        join(token1, '') #empty channel_id

def test_join_invalid_chid():
    '''input error when channel_id doesn't exist'''
    _, token1, _, _, _, _ = create_backend()
    with pytest.raises(InputError):
        join(token1, 100)

def test_join_accesserror():
    '''Trying to join a private channel'''
    _, _, _, _, _, priv_channel = create_backend()
    user3 = auth_register('waydensmith@gmail.com', 'w4yd3nsm1th', 'Wayden', 'Smith')
    token3 = user3['token']
    with pytest.raises(AccessError):
        join(token3, priv_channel) #channel is private

def test_join_invalidtoken():
    '''access error when token is invalid'''
    _, _, _, _, _, priv_channel = create_backend()
    with pytest.raises(AccessError):
        join('invalid_token', priv_channel)

def test_join_flockr_owner():
    '''Joining a private channel as flockr owner'''
    _, token1, _, _, _, priv_channel = create_backend()
    join(token1, priv_channel) #can join because owner of flockr
    u_id1_channels = channels_list(token1)
    if priv_channel != u_id1_channels['channels'][1]['channel_id']:
        raise Exception("Failed")

def test_join_success():
    '''normal user joining a public channel'''
    _, _, _, token2, valid_channel, _ = create_backend()
    join(token2, valid_channel)
    u_id2_channels = channels_list(token2)
    if valid_channel != u_id2_channels['channels'][0]['channel_id']:
        raise Exception("Failed")

def test_joined_already():
    '''trying to join a channel they're already in'''
    _, token1, _, _, valid_channel, _ = create_backend()
    u_id1_channels = channels_list(token1)
    u_id1_channels_num_before = len(u_id1_channels['channels'])
    join(token1, valid_channel)
    u_id1_channels_num_after = len(u_id1_channels['channels'])
    if u_id1_channels_num_before != u_id1_channels_num_after:
        raise Exception("Failed")

'''
Tests for addowner
'''
def test_addowner_ok():
    clear()
    user1 = auth_register("aa@a.com", "123456", "abc", "def")
    user2 = auth_register("bb@a.com", "123456", "efg", "hij")
    channel_id = channels_create(user1['token'], "channel", True)
    join(user2['token'], channel_id['channel_id'])
    addowner(user1['token'], channel_id['channel_id'], user2['u_id'])
    assert details(user1['token'], channel_id['channel_id']) == \
    {
        'name':db['channels'][channel_id['channel_id']]['name'],
        'owner_members': [{'u_id': user1['u_id'], 'name_first': 'abc', 'name_last': 'def', 'profile_img_url': None}, 
        {'u_id': user2['u_id'], 'name_first': 'efg', 'name_last': 'hij', 'profile_img_url': None}],
        'all_members': [{'u_id': user1['u_id'], 'name_first': 'abc', 'name_last': 'def', 'profile_img_url': None}, 
        {'u_id': user2['u_id'], 'name_first': 'efg', 'name_last': 'hij', 'profile_img_url': None}]
    }

def test_addowner_invalid_channelID():
    clear()
    user1 = auth_register("aa@a.com", "123456", "abc", "def")
    with pytest.raises(InputError):
        addowner(user1['token'], 1234, user1['u_id'])
        
def test_addowner_user_already_owner():
    clear()
    user1 = auth_register("aa@a.com", "123456", "abc", "def")
    channel_id = channels_create(user1['token'], "channel", True)
    with pytest.raises(InputError):
        addowner(user1['token'], channel_id['channel_id'], user1['u_id'])
        
def test_addowner_user_not_owner():
    clear()
    user1 = auth_register("aa@a.com", "123456", "abc", "def")
    user2 = auth_register("bb@a.com", "123456", "efg", "hij")
    channel_id = channels_create(user1['token'], "channel", True)
    with pytest.raises(AccessError):
        addowner(user2['token'], channel_id['channel_id'], user2['u_id'])

'''
Tests for removeowner
'''
def test_removeowner_self():
    clear()
    user1 = auth_register("aa@a.com", "123456", "abc", "def")
    channel_id = channels_create(user1['token'], "channel", True)
    removeowner(user1['token'], channel_id['channel_id'], user1['u_id'])

def test_removeowner_other():
    clear()
    user1 = auth_register("aa@a.com", "123456", "abc", "def")
    user2 = auth_register("bb@a.com", "123456", "efg", "hij")
    channel_id = channels_create(user1['token'], "channel", True)
    addowner(user1['token'], channel_id['channel_id'], user2['u_id'])
    removeowner(user1['token'], channel_id['channel_id'], user2['u_id'])

def test_removeowner_invalid_channelID():
    clear()
    user1 = auth_register("aa@a.com", "123456", "abc", "def")
    with pytest.raises(InputError):
        removeowner(user1['token'], 1234, user1['u_id'])
        
def test_removeowner_user_not_owner():
    clear()
    user1 = auth_register("aa@a.com", "123456", "abc", "def")
    user2 = auth_register("bb@a.com", "123456", "efg", "hij")
    channel_id = channels_create(user1['token'], "channel", True)
    with pytest.raises(AccessError):
        removeowner(user2['token'], channel_id['channel_id'], user1['u_id'])
