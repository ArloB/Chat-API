'''
Message HTTP Tests
'''
import requests
import json
import time
from other import clear

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

USER_DATA3 = {
    'email': 'kaydensmith@gmail.com',
    'password': 'k4yd3nsm1th',
    'name_first': 'Kayden',
    'name_last': 'Smith'
}

def settingup(url):
    '''
    Helper function to create a database to test channel and message functions
    '''
    clear()
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

#HTTP Tests for message_send

def test_send_inputerror(url):
    '''testing message send when message has more than 1000 characters'''
    _, token, _, _, ch_id, _ = settingup(url)
    message = 'x'
    for i in range(1000):
        message += str(i)

    data = {
        'token': token,
        'channel_id': ch_id,
        'message': message
    }

    r = requests.post(url + 'message/send', json=data)
    assert r.status_code == 400

def test_send_accesserror1(url):
    '''Access error when sender not part of channel'''
    _, _, _, token, ch_id, _ = settingup(url)
    data1 = {
        'token': token,
        'channel_id': ch_id,
        'message': "hi"
    }
    r1 = requests.post(url + 'message/send', json=data1)
    assert r1.status_code == 400

def test_send_accesserror2(url):
    '''Access error when invalid token'''
    _, _, _, _, ch_id, _ = settingup(url)
    data2 = {
        'token': 'notvalid',
        'channel_id': ch_id,
        'message': "hi"
    }
    r2 = requests.post(url + 'message/send', json=data2)
    assert r2.status_code == 400

def test_send_one(url):
    '''testing that a message has been sent successfully sent to the correct channel'''
    _, token, _, _, ch_id, _ = settingup(url)
    data = {
        'token': token,
        'channel_id': ch_id,
        'message': "hewo"
    }
    response = requests.post(url + 'message/send', json=data)
    assert response.status_code == 200
    result = response.json()
    m_id = result['message_id']
    assert result == {'message_id': m_id}
    message = {
        'token': token,
        'channel_id':ch_id,
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=message)
    assert response.status_code == 200

def test_send_multiple(url):
    '''testing multiple messages can be sent by different users to a channel'''
    _, token1, _, token2, ch_id, _ = settingup(url)
    url_send = url + 'message/send'
    url_messages = url + 'channel/messages'
    data1 = {
        'token': token1,
        'channel_id':ch_id,
        'message': "how are you"
    }
    data2 = {
        'token': token2,
        'channel_id':ch_id,
        'message': "im good thank you"
    }
    data3 = {
        'token': token1,
        'channel_id':ch_id,
        'message': "hi good thank you"
    }
    requests.post(url + 'channel/join', json={'token': token2, 'channel_id': ch_id})
    #assert return values
    r1 = requests.post(url_send, json=data1)
    m_id1 = r1.json()
    message_id1 = m_id1['message_id']
    assert m_id1 == {'message_id': message_id1}
    r2 = requests.post(url_send, json=data2)
    m_id2 = r2.json()
    message_id2 = m_id2['message_id']
    assert m_id2 == {'message_id': message_id2}
    r3 = requests.post(url_send, json=data3)
    m_id3 = r3.json()
    message_id3 = m_id3['message_id']
    assert m_id3 == {'message_id': message_id3}

    resp = requests.get(url_messages, params={'token': token1, 'channel_id':ch_id, 'start': 0})
    assert resp.status_code == 200

#HTTP Tests for message_remove

def test_remove_inputerror1(url):
    '''Input error when no message_id'''
    _, token, _, _, _, _ = settingup(url)
    url_remove = url + 'message/remove'
    data1 = {
        'token': token,
        'message_id': ''
    }
    r1 = requests.delete(url_remove, json=data1)
    assert r1.status_code == 400

def test_remove_inputerror2(url):
    '''Input error when invalid message_id'''
    _, token, _, _, _, _ = settingup(url)
    url_remove = url + 'message/remove'
    data2 = {
        'token': token,
        'message_id': 9
    }
    r2 = requests.delete(url_remove, json=data2)
    assert r2.status_code == 400

def test_remove_accesserror1(url):
    '''Access error when did not create message 
    and is not owner of channel nor flockr'''
    #sending a message to remove
    _, token1, _, token2, ch_id, _ = settingup(url)
    data_add_message = {
        'token': token1,
        'channel_id': ch_id,
        'message': 'hewo'
    }
    r1 = requests.post(url + 'message/send', json=data_add_message)
    assert r1.status_code == 200
    result = r1.json()
    m_id = result['message_id']
    #attempting to delete the sent message
    data_remove_message1 = {
        'token': token2,
        'message_id': m_id
    }
    r2 = requests.delete(url + 'message/remove', json=data_remove_message1)
    assert r2.status_code == 400

def test_remove_accesserror2(url):
    '''Access error when invalid token'''
    #sending a message to remove
    _, token1, _, _, ch_id, _ = settingup(url)
    data_add_message = {
        'token': token1,
        'channel_id': ch_id,
        'message': 'hewo'
    }
    r1 = requests.post(url + 'message/send', json=data_add_message)
    assert r1.status_code == 200
    result = r1.json()
    m_id = result['message_id']
    #attempting to delete the sent message
    data_remove_message2 = {
        'token': 'notvalid',
        'message_id': m_id
    }
    r2 = requests.delete(url + 'message/remove', json=data_remove_message2)
    assert r2.status_code == 400

def test_remove_success(url):
    '''testing if user removing message they sent is successful'''
    _, token, _, _, ch_id, _ = settingup(url)
    #sending a msg
    data_send_message = {
        'token': token,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    r1 = requests.post(url + 'message/send', json=data_send_message)
    assert r1.status_code == 200
    result = r1.json()
    message_id = result['message_id']
    #deleting the message
    data_remove_message = {
        'token': token,
        'message_id': message_id
    }
    r2 = requests.delete(url + 'message/remove', json=data_remove_message)
    assert r2.status_code == 200

def test_remove_by_channel_owner(url):
    '''testing if a channel owner can remove any message'''
    _, token1, u_id2, token2, ch_id, _ = settingup(url)
    data_addowner = {
        'token': token1,
        'channel_id': ch_id,
        'u_id': u_id2
    }
    r1 = requests.post(url + 'channel/addowner', json=data_addowner)
    assert r1.status_code == 200
    #send message
    data_send_message = {
        'token': token1,
        'channel_id': ch_id,
        'message': 'hewo'
    }
    r2 = requests.post(url + 'message/send', json=data_send_message)
    assert r2.status_code == 200
    result = r2.json()
    m_id = result['message_id']
    #remove message
    data_remove_message = {
        'token': token2,
        'message_id': m_id
    }
    r3 = requests.delete(url + 'message/remove', json=data_remove_message)
    assert r3.status_code == 200

def test_remove_by_flockr_owner(url):
    '''testing if flockr owner can remove any message'''
    _, token1, _, token2, _, _ = settingup(url)
    #user2 creates a new channel
    data_channels_create = {
        'token': token2,
        'name': 'Angy',
        'is_public': True
    }
    response = requests.post(url + 'channels/create', json=data_channels_create)
    assert response.status_code == 200
    channel_id2 = response.json()
    ch_id2 = channel_id2['channel_id']
    #user2 sending message
    data_send_message = {
        'token': token2,
        'channel_id': ch_id2,
        'message': 'beepboop'
    }
    r1 = requests.post(url + 'message/send', json=data_send_message)
    assert r1.status_code == 200
    result = r1.json()

    m_id = result['message_id']
    #flockr owner deletes the message
    data_remove_message = {
        'token': token1,
        'message_id': m_id
    }
    r2 = requests.delete(url + 'message/remove', json=data_remove_message)
    assert r2.status_code == 200

#HTTP Tests for message_edit

def test_edit_accesserror1(url):
    '''Access error when user editing message did not 
    create it and is not owner of channel nor flockr'''
    _, token1, _, token2, ch_id, _ = settingup(url)
    url_edit = url + 'message/edit'
    #sending a msg
    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    r1 = requests.post(url + 'message/send', json=data_send_message)
    assert r1.status_code == 200
    result = r1.json()
    message_id = result['message_id']

    data_edit_message1 = {
        'token': token2,
        'message_id': message_id,
        'message': 'hello'
    }
    r2 = requests.put(url_edit, json=data_edit_message1)
    assert r2.status_code == 400

def test_edit_accesserror2(url):
    '''Access error when invalid token'''
    _, token1, _, _, ch_id, _ = settingup(url)
    url_edit = url + 'message/edit'
    #sending a msg
    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    r1 = requests.post(url + 'message/send', json=data_send_message)
    assert r1.status_code == 200
    result = r1.json()
    message_id = result['message_id']
    data_edit_message2 = {
        'token': 'notvalid',
        'message_id': message_id,
        'message': 'hello'
    }
    r2 = requests.put(url_edit, json=data_edit_message2)
    assert r2.status_code == 400

def test_edit_success(url):
    '''testing if user editing their message is successful'''
    _, token, _, _, ch_id, _ = settingup(url)
    #sending a msg
    data_send_message = {
        'token': token,
        'channel_id': ch_id,
        'message': 'hewo'
    }
    r1 = requests.post(url + 'message/send', json=data_send_message)
    assert r1.status_code == 200
    result = r1.json()
    message_id = result['message_id']
    #editing the message
    data_edit_message = {
        'token': token,
        'message_id': message_id,
        'message': 'hello'
    }
    r2 = requests.put(url + 'message/edit', json=data_edit_message)
    assert r2.status_code == 200

def test_edit_by_channel_owner(url):
    '''testing if a channel owner can edit any message'''
    _, token1, u_id2, token2, ch_id, _ = settingup(url)
    #making user2 an owner
    data_addowner = {
        'token': token1,
        'channel_id': ch_id,
        'u_id': u_id2
    }
    requests.post(url + 'channel/addowner', json=data_addowner)
    #user1 sends a message
    data_send_message = {
        'token': token1,
        'channel_id': ch_id,
        'message': 'hewo'
    }
    r1 = requests.post(url + 'message/send', json=data_send_message)
    assert r1.status_code == 200
    result = r1.json()
    message_id = result['message_id']
    #user2 edits the message
    data_edit_message = {
        'token': token2,
        'message_id': message_id,
        'message': 'hello'
    }
    r2 = requests.put(url + 'message/edit', json=data_edit_message)
    assert r2.status_code == 200

def test_edit_by_flockr_owner(url):
    '''testing if flockr owner can edit any message'''
    _, token1, _, token2, _, priv_ch = settingup(url)
    #user2 sends a message
    data_send_message = {
        'token': token2,
        'channel_id': priv_ch,
        'message': 'beepboop'
    }
    r1 = requests.post(url + 'message/send', json=data_send_message)
    assert r1.status_code == 200
    result = r1.json()
    m_id = result['message_id']
    #checks message has been added via channel messages
    data_messages = {
        'token': token2,
        'channel_id': priv_ch,
        'start': 0
    }
    r2 = requests.get(url + 'channel/messages', params=data_messages)
    assert r2.status_code == 200
    result = r2.json()
    #flockr owner edits message
    data_edit_message = {
        'token': token1,
        'message_id': m_id,
        'message': 'hello'
    }
    r3 = requests.put(url + 'message/edit', json=data_edit_message)
    assert r3.status_code == 200

#HTTP Tests for message_pin

def test_pin_input_error1(url):
    '''input error when message_id is invalid'''
    _, token1, _, _, _, _ = settingup(url)
    data = {
        'token': token1,
        'message_id': -1
    }
    r = requests.post(url + 'message/pin', json=data)
    assert r.status_code == 400

def test_pin_input_error2(url):
    '''input error when message already pinned'''
    _, token1, _, _, ch_id, _ = settingup(url)
    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    response = requests.post(url + 'message/send', json=data_send_message)
    result = response.json()
    assert response.status_code == 200
    data = {
        'token': token1,
        'message_id': result['message_id']
    }
    r = requests.post(url + 'message/pin', json=data)
    assert r.status_code == 200
    r = requests.post(url + 'message/pin', json=data)
    assert r.status_code == 400

def test_pin_access_error1(url):
    '''access error when user not part of channel'''
    _, token1, _, token2, ch_id, _ = settingup(url)
    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    response = requests.post(url + 'message/send', json=data_send_message)
    result = response.json()
    assert response.status_code == 200
    data = {
        'token': token2,
        'message_id': result['message_id']
    }
    r = requests.post(url + 'message/pin', json=data)
    assert r.status_code == 400

def test_pin_access_error2(url):
    '''access error when user not owner of channel'''
    _, token1, _, token2, ch_id, _ = settingup(url)
    data_join = {
        'token': token2,
        'channel_id': ch_id
    }
    response = requests.post(url + 'channel/join', json=data_join)
    assert response.status_code == 200

    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    response = requests.post(url + 'message/send', json=data_send_message)
    result = response.json()
    assert response.status_code == 200
    data = {
        'token': token2,
        'message_id': result['message_id']
    }
    r = requests.post(url + 'message/pin', json=data)
    assert r.status_code == 400

def test_pin_success(url):
    '''confirms message was successfully pinned'''
    _, token1, _, _, ch_id, _ = settingup(url)
    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    response = requests.post(url + 'message/send', json=data_send_message)
    result = response.json()
    assert response.status_code == 200
    data = {
        'token': token1,
        'message_id': result['message_id']
    }
    r = requests.post(url + 'message/pin', json=data)
    assert r.status_code == 200

#HTTP Tests for message_sendlater

def test_sendlater_input_error1(url):
    '''input error when text over 1000 characters'''
    _, token, _, _, ch_id, _ = settingup(url)
    message = 'x'
    for i in range(1000):
        message += str(i)

    data = {
        'token': token,
        'channel_id': ch_id,
        'message': message,
        'time_sent': int(time.time() + 1)
    }

    r = requests.post(url + 'message/sendlater', json=data)
    assert r.status_code == 400

def test_sendlater_input_error2(url):
    '''input error when invalid channel_id'''
    _, token, _, _, _, _ = settingup(url)

    data = {
        'token': token,
        'channel_id': 1000,
        'message': 'x',
        'time_sent': int(time.time() + 10)
    }

    r = requests.post(url + 'message/sendlater', json=data)
    assert r.status_code == 400

def test_sendlater_input_error3(url):
    '''input error time is in the past'''
    _, token, _, _, channel_id, _ = settingup(url)

    data = {
        'token': token,
        'channel_id': channel_id,
        'message': 'x',
        'time_sent': int(time.time() - 10000)
    }

    r = requests.post(url + 'message/sendlater', json=data)
    assert r.status_code == 400

def test_sendlater_access_error1(url):
    '''access error when invalid token'''
    _, _, _, _, ch_id, _ = settingup(url)
    data = {
        'token': 'notvalid',
        'channel_id': ch_id,
        'message': "hi",
        'time_sent': int(time.time()) + 10
    }
    r = requests.post(url + 'message/sendlater', json=data)
    assert r.status_code == 400

def test_sendlater_access_error2(url):
    '''access error when user is not in the channel'''
    _, _, _, token, channel_id, _ = settingup(url)

    data = {
        'token': token,
        'channel_id': channel_id,
        'message': 'x',
        'time_sent': int(time.time() + 1)
    }

    r = requests.post(url + 'message/sendlater', json=data)
    assert r.status_code == 400

def test_sendlater_single_success(url):
    '''successfuly sends a message at required time'''
    _, token, _, _, channel_id, _ = settingup(url)
    later_time = int(time.time()) + 1
    data = {
        'token': token,
        'channel_id': channel_id,
        'message': 'x',
        'time_sent': later_time
    }
    r = requests.post(url + 'message/sendlater', json=data)
    assert r.status_code == 200

def test_sendlater_multiple_success(url):
    '''successfuly sends lots of messages at different times'''
    _, token, _, _, channel_id, _ = settingup(url)
    m_one = 'i'
    m_two = 'love'
    m_three = 'u'
    time_two = int(time.time()) + 5
    time_three = int(time.time()) + 10

    data1 = {
        'token': token,
        'channel_id': channel_id,
        'message': m_one,
    }
    data2 = {
        'token': token,
        'channel_id': channel_id,
        'message': m_two,
        'time_sent': time_two
    }
    data3 = {
        'token': token,
        'channel_id': channel_id,
        'message': m_three,
        'time_sent': time_three
    }
    r = requests.post(url + 'message/sendlater', json=data3)
    assert r.status_code == 200
    r = requests.post(url + 'message/send', json=data1)
    assert r.status_code == 200
    r = requests.post(url + 'message/sendlater', json=data2)
    assert r.status_code == 200

#HTTP Tests for message_unpin

def test_unpin_input_error1(url):
    '''input error when message_id is invalid'''
    _, token1, _, _, _, _ = settingup(url)
    data = {
        'token': token1,
        'message_id': -1
    }
    r = requests.post(url + 'message/unpin', json=data)
    assert r.status_code == 400

def test_unpin_input_error2(url):
    '''input error when message already unpinned'''
    _, token1, _, _, ch_id, _ = settingup(url)
    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    response = requests.post(url + 'message/send', json=data_send_message)
    result = response.json()
    assert response.status_code == 200
    data = {
        'token': token1,
        'message_id': result['message_id']
    }
    r = requests.post(url + 'message/unpin', json=data)
    assert r.status_code == 400

def test_unpin_access_error1(url):
    '''access error when user not part of channel'''
    _, token1, _, token2, ch_id, _ = settingup(url)
    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    response = requests.post(url + 'message/send', json=data_send_message)
    result = response.json()
    assert response.status_code == 200
    data = {
        'token': token2,
        'message_id': result['message_id']
    }
    r = requests.post(url + 'message/unpin', json=data)
    assert r.status_code == 400

def test_unpin_access_error2(url):
    '''access error when user not owner of channel'''
    _, token1, _, token2, ch_id, _ = settingup(url)
    data_join = {
        'token': token2,
        'channel_id': ch_id
    }
    response = requests.post(url + 'channel/join', json=data_join)
    assert response.status_code == 200

    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    response = requests.post(url + 'message/send', json=data_send_message)
    result = response.json()
    assert response.status_code == 200
    data = {
        'token': token2,
        'message_id': result['message_id']
    }
    r = requests.post(url + 'message/unpin', json=data)
    assert r.status_code == 400

def test_unpin_success(url):
    '''confirms message was successfully unpinned'''
    _, token1, _, _, ch_id, _ = settingup(url)
    data_send_message = {
        'token': token1,
        'channel_id':ch_id,
        'message': 'hewo'
    }
    response = requests.post(url + 'message/send', json=data_send_message)
    result = response.json()
    assert response.status_code == 200
    data = {
        'token': token1,
        'message_id': result['message_id']
    }
    r = requests.post(url + 'message/pin', json=data)
    assert r.status_code == 200
    r = requests.post(url + 'message/unpin', json=data)
    assert r.status_code == 200

#Tests for message_react

def test_react_empty_mid(url):
    '''input error when message id is empty'''
    _, token, _, _, _, _ = settingup(url)
    data = {
        'token': token,
        'message_id': '',
        'react_id': 1
    }
    r = requests.post(url + 'message/react', json=data)
    assert r.status_code == 400

def test_react_invalid_mid(url):
    '''input error when message id is invalid'''
    _, token, _, _, _, _ = settingup(url)
    data = {
        'token': token,
        'message_id': 99,
        'react_id': 1
    }
    r = requests.post(url + 'message/react', json=data)
    assert r.status_code == 400

def test_react_invalid_reactid(url):
    '''input error when react id is invalid'''
    _, token, _, _, ch_id, _ = settingup(url)
    data_send = {
        'token': token,
        'channel_id': ch_id,
        'message': "hewo"
    }
    r1 = requests.post(url + 'message/send', json=data_send)
    assert r1.status_code == 200
    result = r1.json()
    m_id = result['message_id']

    data = {
        'token': token,
        'message_id': m_id,
        'react_id': 99
    }
    r2 = requests.post(url + 'message/react', json=data)
    assert r2.status_code == 400

def test_react_own(url):
    '''user successfully thumbs up their own message'''
    _, token, _, _, ch_id, _ = settingup(url)
    data_send = {
        'token': token,
        'channel_id': ch_id,
        'message': "hewo"
    }
    r1 = requests.post(url + 'message/send', json=data_send)
    assert r1.status_code == 200
    result = r1.json()
    m_id = result['message_id']

    data = {
        'token': token,
        'message_id': m_id,
        'react_id': 1
    }
    r2 = requests.post(url + 'message/react', json=data)
    assert r2.status_code == 200

def test_react_already_reacted(url):
    '''input error when user tries to react 
    to a message they already reacted to'''
    _, token, _, _, ch_id, _ = settingup(url)
    data_send = {
        'token': token,
        'channel_id': ch_id,
        'message': "hewo"
    }
    r1 = requests.post(url + 'message/send', json=data_send)
    assert r1.status_code == 200
    result = r1.json()
    m_id = result['message_id']

    data = {
        'token': token,
        'message_id': m_id,
        'react_id': 1
    }
    r2 = requests.post(url + 'message/react', json=data)
    assert r2.status_code == 200

    r3 = requests.post(url + 'message/react', json=data)
    assert r3.status_code == 400

def test_react_other(url):
    '''user reacting to someone else's message'''
    #check channel messages-reacts
    _, token1, _, token2, ch_id, _ = settingup(url)
    data = {
        'token': token2,
        'channel_id': ch_id
    }
    r = requests.post(url + 'channel/join', json=data)
    assert r.status_code == 200

    data_send = {
        'token': token1,
        'channel_id': ch_id,
        'message': "hewo"
    }
    r1 = requests.post(url + 'message/send', json=data_send)
    assert r1.status_code == 200
    result = r1.json()
    m_id = result['message_id']

    data = {
        'token': token2,
        'message_id': m_id,
        'react_id': 1
    }
    r2 = requests.post(url + 'message/react', json=data)
    assert r2.status_code == 200

def test_react_multiple(url):
    '''more than one person reacting to messages'''
    #check channel messages-reacts
    _, token1, _, token2, ch_id, _ = settingup(url)
    user1 = requests.post(url + 'auth/register', json=USER_DATA3)
    user1.status_code == 200
    u_1 = user1.json()
    _, token3 = u_1['u_id'], u_1['token']

    data1 = {
        'token': token2,
        'channel_id': ch_id
    }
    r1 = requests.post(url + 'channel/join', json=data1)
    assert r1.status_code == 200

    data2 = {
        'token': token3,
        'channel_id': ch_id
    }
    r2 = requests.post(url + 'channel/join', json=data2)
    assert r2.status_code == 200

    data_send = {
        'token': token2,
        'channel_id': ch_id,
        'message': "hewo"
    }
    r3 = requests.post(url + 'message/send', json=data_send)
    assert r3.status_code == 200
    result = r3.json()
    m_id = result['message_id']

    data_send = {
        'token': token3,
        'channel_id': ch_id,
        'message': "hey"
    }
    r4 = requests.post(url + 'message/send', json=data_send)
    assert r4.status_code == 200

    data = {
        'token': token3,
        'message_id': m_id,
        'react_id': 1
    }
    r5 = requests.post(url + 'message/react', json=data)
    assert r5.status_code == 200

    data = {
        'token': token1,
        'message_id': m_id,
        'react_id': 1
    }
    r6 = requests.post(url + 'message/react', json=data)
    assert r6.status_code == 200

#Tests for message_unreact

def test_unreact_empty_mid(url):
    '''input error when message id is empty'''
    _, token, _, _, _, _ = settingup(url)
    data = {
        'token': token,
        'message_id': '',
        'react_id': 1
    }
    r = requests.post(url + 'message/unreact', json=data)
    assert r.status_code == 400

def test_unreact_invalid_mid(url):
    '''input error when message id is invalid'''
    _, token, _, _, _, _ = settingup(url)
    data = {
        'token': token,
        'message_id': 99,
        'react_id': 1
    }
    r = requests.post(url + 'message/unreact', json=data)
    assert r.status_code == 400

def test_unreact_invalid_reactid(url):
    '''input error when react id is invalid'''
    _, token, _, _, ch_id, _ = settingup(url)
    data_send = {
        'token': token,
        'channel_id': ch_id,
        'message': "hewo"
    }
    response = requests.post(url + 'message/send', json=data_send)
    assert response.status_code == 200
    result = response.json()
    m_id = result['message_id']

    data_react = {
        'token': token,
        'message_id': m_id,
        'react_id': 1
    }
    r = requests.post(url + 'message/react', json=data_react)
    assert r.status_code == 200
    data_unreact = {
        'token': token,
        'message_id': m_id,
        'react_id': 9
    }
    r = requests.post(url + 'message/unreact', json=data_unreact)
    assert r.status_code == 400

def test_unreact_no_reacts(url):
    '''input error when user tries to unreact
    to a message that they didn't react to'''
    _, token, _, _, ch_id, _ = settingup(url)
    data_send = {
        'token': token,
        'channel_id': ch_id,
        'message': "hewo"
    }
    response = requests.post(url + 'message/send', json=data_send)
    assert response.status_code == 200
    result = response.json()
    m_id = result['message_id']

    data_unreact = {
        'token': token,
        'message_id': m_id,
        'react_id': 1
    }
    r = requests.post(url + 'message/unreact', json=data_unreact)
    assert r.status_code == 400

def test_unreact_success(url):
    '''user unreacting to their own message'''
    _, token, _, _, ch_id, _ = settingup(url)
    data_send = {
        'token': token,
        'channel_id': ch_id,
        'message': "hewo"
    }
    response = requests.post(url + 'message/send', json=data_send)
    assert response.status_code == 200
    result = response.json()
    m_id = result['message_id']

    data_react = {
        'token': token,
        'message_id': m_id,
        'react_id': 1
    }
    r = requests.post(url + 'message/react', json=data_react)
    assert r.status_code == 200
    data_unreact = {
        'token': token,
        'message_id': m_id,
        'react_id': 1
    }
    r = requests.post(url + 'message/unreact', json=data_unreact)
    assert r.status_code == 200

def test_unreact_multiple(url):
    '''multiple users reacting to a message then
    one user unreacts'''
    _, token1, _, token2, ch_id, _ = settingup(url)
    user1 = requests.post(url + 'auth/register', json=USER_DATA3)
    user1.status_code == 200
    u_1 = user1.json()
    _, token3 = u_1['u_id'], u_1['token']
    
    data1 = {
        'token': token2,
        'channel_id': ch_id
    }
    r1 = requests.post(url + 'channel/join', json=data1)
    assert r1.status_code == 200

    data2 = {
        'token': token3,
        'channel_id': ch_id
    }
    r2 = requests.post(url + 'channel/join', json=data2)
    assert r2.status_code == 200

    data_send = {
        'token': token2,
        'channel_id': ch_id,
        'message': "hewo"
    }
    response = requests.post(url + 'message/send', json=data_send)
    assert response.status_code == 200
    result = response.json()
    m_id = result['message_id']

    data_react = {
        'token': token3,
        'message_id': m_id,
        'react_id': 1
    }
    r = requests.post(url + 'message/react', json=data_react)
    assert r.status_code == 200

    data_react = {
        'token': token1,
        'message_id': m_id,
        'react_id': 1
    }
    r = requests.post(url + 'message/react', json=data_react)
    assert r.status_code == 200

    data_react = {
        'token': token2,
        'message_id': m_id,
        'react_id': 1
    }
    r = requests.post(url + 'message/react', json=data_react)
    assert r.status_code == 200

    data_unreact = {
        'token': token1,
        'message_id': m_id,
        'react_id': 1
    }
    r = requests.post(url + 'message/unreact', json=data_unreact)
    assert r.status_code == 200

    data_unreact = {
        'token': token3,
        'message_id': m_id,
        'react_id': 1
    }
    r = requests.post(url + 'message/unreact', json=data_unreact)
    assert r.status_code == 200
