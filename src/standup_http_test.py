'''Tests for standup functions'''
from time import time, sleep
import requests
import pytest

from other import clear

# Standup/start tests

def test_standup_start_valid(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": user['token'], "name": "channel", "is_public": True}).json()
    seconds = int(time())
    standup = requests.post(f"{url}/standup/start", json={'token': user['token'], 'channel_id': channel['channel_id'], 'length': 5}).json()
    assert standup['time_finish'] == seconds + 5

def test_standup_start_invalid_token(url):
    clear()
    assert requests.post(f"{url}/standup/start", json={'token': '12345', 'channel_id': 0, 'length': 5}).status_code == 400

def test_standup_start_invalid_channelid(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    assert requests.post(f"{url}/standup/start", json={'token': user['token'], 'channel_id': 0, 'length': 5}).status_code == 400

def test_standup_start_started_already(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": user['token'], "name": "channel", "is_public": True}).json()
    assert requests.post(f"{url}/standup/start", json={'token': user['token'], 'channel_id': channel['channel_id'], 'length': 5}).status_code == 200
    assert requests.post(f"{url}/standup/start", json={'token': user['token'], 'channel_id': channel['channel_id'], 'length': 5}).status_code == 400
    

# Test standup/active

def test_standup_active_true(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": user['token'], "name": "channel", "is_public": True}).json()
    standup = requests.post(f"{url}/standup/start", json={'token': user['token'], 'channel_id': channel['channel_id'], 'length': 5}).json()
    res = requests.get(f"{url}/standup/active", params={'token': user['token'], 'channel_id': channel['channel_id']}).json() 
    assert res == {'is_active': True, 'time_finish': standup['time_finish']}
    

def test_standup_active_false(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": user['token'], "name": "channel", "is_public": True}).json()
    assert requests.get(f"{url}/standup/active", params={'token': user['token'], 'channel_id': channel['channel_id']}).json() == {'is_active': False, 'time_finish': None}

def test_standup_active_invalid_token(url):
    clear()
    assert requests.get(f"{url}/standup/active", params={'token': '1234', 'channel_id': 0}).status_code == 400


def test_standup_active_invalid_channelid(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    assert requests.get(f"{url}/standup/active", params={'token': user['token'], 'channel_id': 0}).status_code == 400

# Test standup/send

def test_standup_send_valid(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": user['token'], "name": "channel", "is_public": True}).json()
    requests.post(f"{url}/standup/start", json={'token': user['token'], 'channel_id': channel['channel_id'], 'length': 5}).json()
    requests.post(f"{url}/standup/send", json={'token': user['token'], 'channel_id': channel['channel_id'], 'message': 'hello'})
    sleep(5)
    handle = requests.get(f"{url}/user/profile", params={'token': user['token'], 'u_id': user['u_id']}).json()['user']['handle_str']
    msg = requests.get(f"{url}/channel/messages", params={'token': user['token'], 'channel_id': channel['channel_id'], 'start': 0}).json()['messages'][0]['message']
    assert msg == f"{handle}: hello"

def test_standup_send_invalid_token(url):
    clear()
    assert requests.post(f"{url}/standup/send", json={'token': '12345', 'channel_id': 0, 'message': 'hello'}).status_code == 400

def test_standup_send_user_not_in_channel(url):
    clear()
    user1 = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    user2 = requests.post(f"{url}/auth/register", json={"email": "bb@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": user1['token'], "name": "channel", "is_public": True}).json()
    requests.post(f"{url}/standup/start", json={'token': user1['token'], 'channel_id': channel['channel_id'], 'length': 5})
    assert requests.post(f"{url}/standup/send", json={'token': user2['token'], 'channel_id': channel['channel_id'], 'message': 'hello'}).status_code == 400

def test_standup_send_invalid_channelid(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": user['token'], "name": "channel", "is_public": True}).json()
    requests.post(f"{url}/standup/start", json={'token': user['token'], 'channel_id': channel['channel_id'], 'length': 5})
    assert requests.post(f"{url}/standup/send", json={'token': user['token'], 'channel_id': 123, 'message': 'hello'}).status_code == 400
    

def test_standup_send_invalid_length(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": user['token'], "name": "channel", "is_public": True}).json()
    requests.post(f"{url}/standup/start", json={'token': user['token'], 'channel_id': channel['channel_id'], 'length': 5})
    assert requests.post(f"{url}/standup/send", json={'token': user['token'], 'channel_id': channel['channel_id'], 'message': "a" * 1001}).status_code == 400
    

def test_standup_send_no_standup(url):
    clear()
    user = requests.post(f"{url}/auth/register", json={"email": "aa@a.com", "password": "123456", "name_first": "a", "name_last": "b"}).json()
    channel = requests.post(f"{url}/channels/create", json={"token": user['token'], "name": "channel", "is_public": True}).json()
    assert requests.post(f"{url}/standup/send", json={'token': user['token'], 'channel_id': channel['channel_id'], 'message': "a"}).status_code == 400