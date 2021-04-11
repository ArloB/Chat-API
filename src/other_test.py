import hashlib
import pytest

from other import *
from auth import auth_register, auth_logout
from channels import channels_create
from message import message_send
from error import *

'''
Tests for users_all
'''

def test_users_all_one():
    clear()
    user_dict = auth_register('user@email.com', 'password', 'first', 'last')
    userslist = users_all(user_dict['token'])
    assert userslist['users'] == [{'u_id': user_dict['u_id'], \
        'handle_str': 'lfirst', 'email': 'user@email.com', 'password': hashlib.sha256("password".encode()).hexdigest(),\
        'name_first': 'first', 'name_last': 'last', 'token': \
        user_dict['token'], 'is_owner': True, 'profile_img_url': None}]

def test_users_all_two():
    clear()
    user_dict1 = auth_register('user@email.com', 'password', 'first', 'last')
    assert auth_logout(user_dict1['token'])['is_success']
    user_dict2 = auth_register('other@gmail.com', 'verystronk', 'apple', 'tree')
    userslist = users_all(user_dict2['token'])
    assert userslist['users'] == [{'u_id': user_dict1['u_id'], \
        'handle_str': 'lfirst', 'email': 'user@email.com', 'password': hashlib.sha256("password".encode()).hexdigest(), \
        'name_first': 'first', 'name_last': 'last', 'token': None, 'is_owner': True, 'profile_img_url': None}, \
        {'u_id': user_dict2['u_id'], 'handle_str': 'tapple', 'email': \
        'other@gmail.com', 'password': hashlib.sha256("verystronk".encode()).hexdigest(), \
        'name_first': 'apple', 'name_last': 'tree', 'token': \
        user_dict2['token'], 'is_owner': False, 'profile_img_url': None}]

def test_users_all_three():
    clear()
    user_dict1 = auth_register('someone@email.com', 'three456', 'bill', 'murray')
    assert auth_logout(user_dict1['token'])['is_success']
    user_dict2 = auth_register('else@gmail.com', 'qwerty123', 'jack', 'rick')
    userslist = users_all(user_dict2['token'])
    assert userslist['users'] == [{'u_id': user_dict1['u_id'], 'handle_str': 'mbill', \
        'email': 'someone@email.com', 'password': hashlib.sha256("three456".encode()).hexdigest(), 'name_first': 'bill', \
        'name_last': 'murray', 'token': None, 'is_owner': True, 'profile_img_url': None}, \
        {'u_id': user_dict2['u_id'], 'handle_str': 'rjack', 'email': 'else@gmail.com', 'password': hashlib.sha256("qwerty123".encode()).hexdigest(), \
        'name_first': 'jack', 'name_last': 'rick', 'token': \
        user_dict2['token'], 'is_owner': False, 'profile_img_url': None}]

'''
Tests for admin_userpermission_change
'''

def test_add_admin_invalid_token():
    '''
    Test adding a user as admin with invalid token
    '''
    clear()
    user = auth_register("aa@a.com", "123456", "a", "b")
    with pytest.raises(InputError):
        admin_userpermission_change("123456", user['u_id'], 2)

def test_add_admin_invalid_uid():
    '''
    Test adding a user as admin with invalid u_id
    '''
    clear()
    user = auth_register("aa@a.com", "123456", "a", "b")
    with pytest.raises(InputError):
        admin_userpermission_change(user['token'], "123", 2)

def test_add_admin_not_owner():
    '''
    Test adding a user as admin by a non-admin user
    '''
    clear()
    user = auth_register("aa@a.com", "123456", "a", "b")
    user2 = auth_register("bb@a.com", "123456", "b", "a")
    with pytest.raises(AccessError):
        admin_userpermission_change(user2['token'], user['u_id'], 2)

def test_add_admin():
    '''
    Test adding a user as admin
    '''
    clear()
    user = auth_register("aa@a.com", "123456", "a", "b")
    user2 = auth_register("bb@a.com", "123456", "b", "a")
    assert admin_userpermission_change(user['token'], user2['u_id'], 2) == {}

def test_remove_admin():
    '''
    Test removing a user's admin permissions
    '''
    clear()
    user = auth_register("aa@a.com", "123456", "a", "b")
    user2 = auth_register("bb@a.com", "123456", "b", "a")
    assert admin_userpermission_change(user['token'], user2['u_id'], 2) == {}
    assert admin_userpermission_change(user['token'], user2['u_id'], 1) == {}

'''
Tests for search
'''

def test_search_no_channels():
    clear()
    user = auth_register("aa@a.com", "123456", "a", "b")
    assert search(user['token'], 'abc') == {"messages": []}

def test_search_no_messages():
    clear()
    user = auth_register("aa@a.com", "123456", "a", "b")
    channels_create(user['token'], 'c1', True)
    assert search(user['token'], 'abc') == {"messages": []}

def test_search_no_user():
    clear()
    assert search('', 'abc') == {"messages": []}

def test_search_two_users():
    clear()
    user = auth_register("aa@a.com", "123456", "a", "b")
    user2 = auth_register("bb@a.com", "123456", "b", "a")
    channel = channels_create(user2['token'], 'c1', True)
    msg = message_send(user2['token'], channel['channel_id'], "hello")
    msg2 = message_send(user2['token'], channel['channel_id'], "Hello")
    assert search(user['token'], 'he') == {"messages": []}
    assert search(user2['token'], 'he')['messages'][0]['message_id'] == msg["message_id"]
    assert search(user2['token'], 'He')['messages'][0]['message_id'] == msg2["message_id"]