from standup import standup_start, standup_active, standup_send
from auth import auth_register
from channels import channels_create
from channel import messages
from other import clear
from user import user_profile
from time import time, sleep
from error import *
from message import message_send
import pytest

# Standup/start tests

def test_standup_start_valid():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    channel = channels_create(user['token'], "channel", True)
    seconds = int(time())
    standup = standup_start(user['token'], channel['channel_id'], 1)
    assert standup['time_finish'] == seconds + 1
    sleep(1)

def test_standup_start_invalid_token():
    clear()
    with pytest.raises(AccessError):
        standup_start('12345', 0, 1)
    sleep(1)

def test_standup_start_invalid_channelid():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    with pytest.raises(InputError):
        standup_start(user['token'], 0, 1)
    sleep(1)

def test_standup_start_started_already():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    channel = channels_create(user['token'], "channel", True)
    standup_start(user['token'], channel['channel_id'], 1)
    with pytest.raises(InputError):
        standup_start(user['token'], channel['channel_id'], 1)
    sleep(2)

# Test standup/active

def test_standup_active_true():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    channel = channels_create(user['token'], "channel", True)
    standup = standup_start(user['token'], channel['channel_id'], 1)
    assert standup_active(user['token'], channel['channel_id']) == { 'is_active': True, 'time_finish': standup['time_finish'] }
    sleep(1)

def test_standup_active_false():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    channel = channels_create(user['token'], "channel", True)
    assert standup_active(user['token'], channel['channel_id']) == { 'is_active': False, 'time_finish': None }

def test_standup_active_invalid_token():
    clear()
    with pytest.raises(AccessError):
        standup_active('12345', 0)

def test_standup_active_invalid_channelid():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    with pytest.raises(InputError):
        standup_active(user['token'], 0)

# Test standup/send

def test_standup_send_valid():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    channel = channels_create(user['token'], "channel", True)
    standup_start(user['token'], channel['channel_id'], 5)
    standup_send(user['token'], channel['channel_id'], "hello")
    sleep(5)
    handle = user_profile(user['token'], user['u_id'])['user']['handle_str']
    assert messages(user['token'], channel['channel_id'], 0)['messages'][0]['message'] == f"{handle}: hello"

def test_standup_send_invalid_token():
    clear()
    with pytest.raises(AccessError):
        standup_send('12345', 0, 'abc')

def test_standup_send_user_not_in_channel():
    clear()
    user1 = auth_register("a@a.com", "123456", "a", "b")
    user2 = auth_register("b@a.com", "123456", "a", "b")
    channel = channels_create(user1['token'], "channel", True)
    standup_start(user1['token'], channel['channel_id'], 1)
    with pytest.raises(AccessError):
        standup_send(user2['token'], channel['channel_id'], "abdxc")
    sleep(1)

def test_standup_send_invalid_channelid():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    channel = channels_create(user['token'], "channel", True)
    standup_start(user['token'], channel['channel_id'], 1)
    with pytest.raises(InputError):
        standup_send(user['token'], 123, "a" * 1001)
    sleep(1)

def test_standup_send_invalid_length():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    channel = channels_create(user['token'], "channel", True)
    standup_start(user['token'], channel['channel_id'], 1)
    with pytest.raises(InputError):
        standup_send(user['token'], channel['channel_id'], "a" * 1001)
    sleep(1)

def test_standup_send_no_standup():
    clear()
    user = auth_register("a@a.com", "123456", "a", "b")
    channel = channels_create(user['token'], "channel", True)
    with pytest.raises(InputError):
        standup_send(user['token'], channel['channel_id'], "a")
