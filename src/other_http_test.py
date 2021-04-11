import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import hashlib
import pytest

@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

'''
Tests for users_all
'''

def test_users_all_one(url):
    register_data = {
        'email': 'user@email.com',
        'password': 'password',
        'name_first': 'first',
        'name_last': 'last'
    }

    url_register = url + 'auth/register'
    url_users_all = url + 'users/all'

    requests.delete(f"{url}/clear")
    resp = requests.post(url_register, json=register_data)
    user_dict = resp.json()
    resp = requests.get(url_users_all, params=user_dict)
    userslist = resp.json()
    assert userslist['users'] == [{'u_id': user_dict['u_id'], \
        'handle_str': 'lfirst', 'email': 'user@email.com', 'password': hashlib.sha256("password".encode()).hexdigest(),\
        'name_first': 'first', 'name_last': 'last', 'token': \
        user_dict['token'], 'is_owner': True, 'profile_img_url': None}]

def test_users_all_two(url):
    register_data1 = {
        'email': 'user@email.com',
        'password': 'password',
        'name_first': 'first',
        'name_last': 'last'
    }
    register_data2 = {
        'email': 'other@gmail.com',
        'password': 'verystronk',
        'name_first': 'apple',
        'name_last': 'tree'
    }

    url_register = url + 'auth/register'
    url_users_all = url + 'users/all'
    url_logout = url + 'auth/logout'

    requests.delete(f"{url}/clear")
    resp = requests.post(url_register, json=register_data1)
    user_dict1 = resp.json()
    resp = requests.post(url_logout, json=user_dict1)
    assert resp.ok
    resp = requests.post(url_register, json=register_data2)
    user_dict2 = resp.json()
    resp = requests.get(url_users_all, params=user_dict2)
    userslist = resp.json()
    assert userslist['users'] == [{'u_id': user_dict1['u_id'], \
        'handle_str': 'lfirst', 'email': 'user@email.com', 'password': hashlib.sha256("password".encode()).hexdigest(), \
        'name_first': 'first', 'name_last': 'last', 'token': None, 'is_owner': True, 'profile_img_url': None}, \
        {'u_id': user_dict2['u_id'], 'handle_str': 'tapple', 'email': \
        'other@gmail.com', 'password': hashlib.sha256("verystronk".encode()).hexdigest(), \
        'name_first': 'apple', 'name_last': 'tree', 'token': \
        user_dict2['token'], 'is_owner': False, 'profile_img_url': None}]

def test_users_all_three(url):
    register_data1 = {
        'email': 'someone@email.com',
        'password': 'three456',
        'name_first': 'bill',
        'name_last': 'murray'
    }
    register_data2 = {
        'email': 'else@gmail.com',
        'password': 'qwerty123',
        'name_first': 'jack',
        'name_last': 'rick'
    }

    url_register = url + 'auth/register'
    url_users_all = url + 'users/all'
    url_logout = url + 'auth/logout'

    requests.delete(f"{url}/clear")
    resp = requests.post(url_register, json=register_data1)
    user_dict1 = resp.json()
    resp = requests.post(url_logout, json=user_dict1)
    assert resp.ok
    resp = requests.post(url_register, json=register_data2)
    user_dict2 = resp.json()
    resp = requests.get(url_users_all, params=user_dict2)
    userslist = resp.json()
    assert userslist['users'] == [{'u_id': user_dict1['u_id'], 'handle_str': 'mbill', \
        'email': 'someone@email.com', 'password': hashlib.sha256("three456".encode()).hexdigest(), 'name_first': 'bill', \
        'name_last': 'murray', 'token': None, 'is_owner': True, 'profile_img_url': None}, \
        {'u_id': user_dict2['u_id'], 'handle_str': 'rjack', 'email': 'else@gmail.com', 'password': hashlib.sha256("qwerty123".encode()).hexdigest(), \
        'name_first': 'jack', 'name_last': 'rick', 'token': \
        user_dict2['token'], 'is_owner': False, 'profile_img_url': None}]

'''
Tests for admin_userpermission_change
'''

def test_add_admin_invalid_token(url):
    '''
    Test adding a user as admin with invalid token
    '''
    requests.delete(f"{url}/clear")
    res = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    assert requests.post(f"{url}/admin/userpermission/change", json={"token": "123456", "u_id": res['u_id'], "permission_id": "2"}).status_code == 400

def test_add_admin_invalid_uid(url):
    '''
    Test adding a user as admin with invalid u_id
    '''
    requests.delete(f"{url}/clear")
    res = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    assert requests.post(f"{url}/admin/userpermission/change", json={"token": res['token'], "u_id": '123', "permission_id": "2"}).status_code == 400

def test_add_admin_not_owner(url):
    '''
    Test adding a user as admin by a non-admin user
    '''
    requests.delete(f"{url}/clear")
    res = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    res2 = requests.post(f"{url}/auth/register", json={"email": "bb@a.com", "password": "123456", "name_first": "b", "name_last": "a"}).json()
    assert requests.post(f"{url}/admin/userpermission/change", json={"token": res2['token'], "u_id": res['u_id'], "permission_id": "2"}).status_code == 400

def test_add_admin(url):
    '''
    Test adding a user as admin
    '''
    requests.delete(f"{url}/clear")
    res = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    res2 = requests.post(f"{url}/auth/register", json={"email": "bb@a.com", "password": "123456", "name_first": "b", "name_last": "a"}).json()
    assert requests.post(f"{url}/admin/userpermission/change", json={"token": res['token'], "u_id": res2['u_id'], "permission_id": "2"}).status_code == 200

def test_remove_admin(url):
    '''
    Test removing a user's admin permissions
    '''
    requests.delete(f"{url}/clear")
    res = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    res2 = requests.post(f"{url}/auth/register", json={"email": "bb@a.com", "password": "123456", "name_first": "b", "name_last": "a"}).json()
    assert requests.post(f"{url}/admin/userpermission/change", json={"token": res['token'], "u_id": res2['u_id'], "permission_id": "2"}).status_code == 200
    assert requests.post(f"{url}/admin/userpermission/change", json={"token": res['token'], "u_id": res2['u_id'], "permission_id": "1"}).status_code == 200

'''
Tests for search
'''

def test_search_no_channels(url):
    requests.delete(f"{url}/clear")
    res = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    assert requests.get(f"{url}/search", params={"token": res['token'], "query_str": "abc"}).json() == {"messages": []}

def test_search_no_messages(url):
    requests.delete(f"{url}/clear")
    res = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    requests.post(f"{url}/channels/create", json={"token": res['token'], "name": "c1", "is_public": True}).json()
    assert requests.get(f"{url}/search", params={"token": res['token'], "query_str": "abc"}).json() == {"messages": []}

def test_search_no_user(url):
    requests.delete(f"{url}/clear")
    assert requests.get(f"{url}/search", params={"token": "", "query_str": "abc"}).json() == {"messages": []}

def test_search_two_users(url):
    requests.delete(f"{url}/clear")
    res = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    res2 = requests.post(f"{url}/auth/register", json={"email": "bb@a.com", "password": "123456", "name_first": "b", "name_last": "a"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": res2['token'], "name": "channel", "is_public": "True"}).json()
    msg = requests.post(f"{url}/message/send", json={"token": res2['token'], "channel_id": channel['channel_id'], "message": "hello"}).json()
    msg2 = requests.post(f"{url}/message/send", json={"token": res2['token'], "channel_id": channel['channel_id'], "message": "Hello"}).json()
    assert requests.get(f"{url}/search", params={"token": res['token'], "query_str": "he"}).json() == {"messages": []}
    assert requests.get(f"{url}/search", params={"token": res2['token'], "query_str": "he"}).json()['messages'][0]['message_id'] == msg["message_id"]
    assert requests.get(f"{url}/search", params={"token": res2['token'], "query_str": "He"}).json()['messages'][0]['message_id'] == msg2["message_id"]


