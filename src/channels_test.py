import channels
import auth
import channel
import other
import pytest
from error import InputError

# Channels_list - Provides list of channels (+ details) that authorised user is part of
# Return - List of dictionaries(channel_id,name)

def test_channels_list_one():
    other.clear()
    user_dict = auth.auth_register('user@email.com', 'password', 'first', 'last')
    _ = user_dict['u_id']
    token = user_dict['token']
    ch_dict = channels.channels_create(token, 'Tree', False)
    ch_id = ch_dict['channel_id']
    assert channels.channels_list(token) == {'channels': [{'name': 'Tree', 'channel_id': ch_id}]}

def test_channels_list_empty():
    other.clear()
    user_dict = auth.auth_register('user@email.com', 'password', 'first', 'last')
    token = user_dict['token']
    assert channels.channels_list(token) == {'channels': []}

def test_channels_list_otheruser(): 
    other.clear()
    user_dict = auth.auth_register('user@email.com', 'password', 'first', 'last')
    _ = user_dict['u_id']
    token = user_dict['token']
    ch_dict = channels.channels_create(token, 'Tree', False)
    ch_id = ch_dict['channel_id']
    auth.auth_logout(token)
    user_dict = auth.auth_register('other@email.com', 'computer', 'Jim', 'Halpert')
    _ = user_dict['u_id']
    token = user_dict['token']    
    ch_dict = channels.channels_create(token, 'Apple', False)
    ch_id = ch_dict['channel_id']
    assert channels.channels_list(token) == {'channels': [{'name': 'Apple', 'channel_id': ch_id}]}



# Channels_listall - Provides list of ALL channels (+ details)
# Return - List of dictionaries(channel_id,name)

def test_channels_listall_one():
    other.clear()
    user_dict = auth.auth_register('user@email.com', 'password', 'first', 'last')
    _ = user_dict['u_id']
    token = user_dict['token']    
    ch_dict = channels.channels_create(token, 'Tree', False)
    ch_id = ch_dict['channel_id']
    assert channels.channels_listall(token) == {'channels': [{'name': 'Tree', 'channel_id': ch_id}]}

def test_channels_listall_two():
    other.clear()
    user_dict = auth.auth_register('user@email.com','password','first', 'last')
    _ = user_dict['u_id']
    token = user_dict['token']
    ch_dict1 = channels.channels_create(token, 'Tree', True)
    ch_id1 = ch_dict1['channel_id']
    ch_dict2 = channels.channels_create(token, 'Apple',True)
    ch_id2 = ch_dict2['channel_id']
    assert channels.channels_listall(token) == {'channels': [{'channel_id': ch_id1, 'name': 'Tree'}, {'channel_id': ch_id2, 'name': 'Apple'}]}

def test_channels_listall_otheruser(): 
    other.clear()
    user_dict = auth.auth_register('user@email.com', 'password', 'first', 'last')
    _ = user_dict['u_id']
    token = user_dict['token']
    ch_dict1 = channels.channels_create(token, 'Tree', False)
    ch_id1 = ch_dict1['channel_id']
    auth.auth_logout(token)
    user_dict = auth.auth_register('other@email.com', 'computer', 'Jim', 'Halpert')
    _ = user_dict['u_id']
    token = user_dict['token']
    ch_dict2 = channels.channels_create(token, 'Apple', False)
    ch_id2 = ch_dict2['channel_id']
    assert channels.channels_listall(token) == {'channels': [{'channel_id': ch_id1, 'name': 'Tree'}, {'channel_id': ch_id2, 'name': 'Apple'}]}


def test_channels_listall_empty():
    other.clear()
    user_dict = auth.auth_register('user@email.com', 'password', 'first', 'last')
    token = user_dict['token']
    assert channels.channels_listall(token) == {'channels': []}

# Channels_create - Creates new channel w/ name, either public or private
# Return - Channel_id
# Input Error - Name is > 20 Characters, No name

def test_channels_create_success():
    other.clear()
    user_dict = auth.auth_register('user@email.com','password','first','last')
    token = user_dict['token']
    ch_dict = channels.channels_create(token,'Test', False)
    ch_id = ch_dict['channel_id']
    assert ch_dict == {'channel_id': ch_id}

def test_channels_create_two():
    other.clear()
    user_dict = auth.auth_register('user@email.com','password','first','last')
    token = user_dict['token']
    ch_dict1 = channels.channels_create(token,'Mango', True)
    ch_id1 = ch_dict1['channel_id']
    ch_dict2 = channels.channels_create(token,'Banana', False)
    ch_id2 = ch_dict2['channel_id']
    assert ch_dict1 == {'channel_id': ch_id1}
    assert ch_dict2 == {'channel_id': ch_id2}

def test_channels_create_too_long_one():
    other.clear()
    user_dict = auth.auth_register('user@email.com','password','first','last')
    token = user_dict['token']
    with pytest.raises(InputError):
        channels.channels_create(token,'Thisnameiswaytoolong123', True)

def test_channels_create_too_long_two():
    other.clear()
    user_dict = auth.auth_register('user@email.com', 'password', 'first', 'last')
    token = user_dict['token']
    channels.channels_create(token,'Apple', True)
    channels.channels_create(token,'Pear', False)
    with pytest.raises(InputError):
        channels.channels_create(token, 'Hellohellohellohellohellohello', True)
