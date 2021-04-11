'''Message test functions'''
import pytest
import time
from error import InputError, AccessError
from other import clear

from message import *

from auth import auth_register
from channel import messages, join, addowner
from channels import channels_create

def setup():
    '''clears data and creates users and channels for testing'''
    clear()
    user1 = auth_register('haydensmith@gmail.com', 'h4yd3nsm1th', \
    'Hayden', 'Smith')
    u_id1 = user1['u_id']
    token1 = user1['token']
    user2 = auth_register('jaydensmith@gmail.com', 'j4yd3nsm1th', \
    'Jayden', 'Smith')
    u_id2 = user2['u_id']
    token2 = user2['token']

    valid_channel = channels_create(token1, 'The Smiths', True)
    valid_channel_id = valid_channel['channel_id']

    return u_id1, token1, u_id2, token2, valid_channel_id

#Tests for message_send

def test_send_inputerror():
    '''testing message send when message has more than 1000 characters'''
    _, token, _, _, channel_id = setup()
    message = 'x'
    for i in range(1000):
        message += str(i)
    with pytest.raises(InputError):
        message_send(token, channel_id, message)

def test_send_invalid_chid():
    '''input error when channel id is not a valid channel'''
    _, _, _, token, _ = setup()
    with pytest.raises(InputError):
        message_send(token, 99, "hi")

def test_send_accesserror():
    '''access error when sender is not part of channel'''
    _, _, _, token, channel_id = setup()
    with pytest.raises(AccessError):
        message_send(token, channel_id, "hi")

def test_send_invalidtoken():
    '''when token is invalid'''
    _, _, _, _, channel_id = setup()
    with pytest.raises(AccessError):
        message_send('invalid_token', channel_id, "hi")

def test_send_one():
    '''testing that a message has been sent successfully sent to the correct channel'''
    _, token, _, _, channel_id = setup()
    m_id = message_send(token, channel_id, "hewo")
    m_dict = messages(token, channel_id, 0)
    assert m_dict['messages'][0]['message_id'] == m_id['message_id']

def test_send_multiple():
    '''testing multiple messages can be sent by different users to a channel'''
    _, token1, _, token2, channel_id = setup()
    join(token2, channel_id)
    m_id1 = message_send(token1, channel_id, "hi")
    m_id2 = message_send(token2, channel_id, "hey")
    m_id3 = message_send(token1, channel_id, "how are you")
    m_id4 = message_send(token2, channel_id, "fine thanks")
    m_dict = messages(token1, channel_id, 0)
    assert m_dict['messages'][3]['message_id'] == m_id1['message_id']
    assert m_dict['messages'][2]['message_id'] == m_id2['message_id']
    assert m_dict['messages'][1]['message_id'] == m_id3['message_id']
    assert m_dict['messages'][0]['message_id'] == m_id4['message_id']

def test_send_with_deletes():
    '''testing messages all have unique ids even when deleting'''
    _, token1, _, _, channel_id = setup()
    m_id1 = message_send(token1, channel_id, "hi")
    message_remove(token1, m_id1['message_id'])
    m_id2 = message_send(token1, channel_id, "hey")
    assert m_id2['message_id'] != m_id1['message_id']

#Tests for message_remove

def test_remove_inputerror():
    #input error if message has already been deleted
    '''if message doesn't exist, inputerror'''
    _, token1, _, _, channel_id = setup()
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    message_remove(token1, message_id)
    with pytest.raises(InputError):
        message_remove(token1, message_id)

def test_remove_accesserror():
    '''if user removing message did not create it and is not owner of channel nor flockr'''
    _, token1, _, token2, channel_id = setup()
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    with pytest.raises(AccessError):
        message_remove(token2, message_id)

def test_remove_invalidtoken():
    '''when token is invalid'''
    _, token1, _, _, channel_id = setup()
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    with pytest.raises(AccessError):
        message_remove('invalid_token', message_id)

def test_remove_invalid_mid():
    '''when message id is invalid'''
    _, token1, _, _, channel_id = setup()
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id ['message_id']
    message_remove(token1, message_id)
    with pytest.raises(AccessError):
        message_remove(token1, 9)

def test_remove_one():
    '''testing if user removing message they sent is successful'''
    _, token1, _, _, channel_id = setup()
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    message_remove(token1, message_id)
    message_dict = messages(token1, channel_id, 0)
    assert message_dict['messages'] == []

def test_remove_multiple():
    '''testing if multiple messages can be removed'''
    _, token1, _, token2, channel_id = setup()
    join(token2, channel_id)
    message_send(token1, channel_id, "hi")
    m_id2 = message_send(token2, channel_id, "hey")
    message_send(token1, channel_id, "how are you")
    m_id4 = message_send(token2, channel_id, "fine thanks")
    message_id2 = m_id2['message_id']
    message_id4 = m_id4['message_id']
    message_remove(token2, message_id2)
    message_remove(token2, message_id4)
    m_dict = messages(token1, channel_id, 0)
    assert m_dict['messages'][1]['message'] == "hi"
    assert m_dict['messages'][0]['message'] == "how are you"

def test_remove_by_channel_owner():
    '''testing if a channel owner can remove any message'''
    _, token1, u_id2, token2, channel_id = setup()
    addowner(token1, channel_id, u_id2)
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    message_remove(token2, message_id)
    message_dict = messages(token1, channel_id, 0)
    assert message_dict['messages'] == []

def test_remove_by_flockr_owner():
    '''testing if flockr owner can remove any message'''
    _, token1, _, token2, _ = setup()
    ch_id2 = channels_create(token2, 'Angy', True)
    channel_id2 = ch_id2['channel_id']
    m_id = message_send(token2, channel_id2, "beepboop")
    message_id = m_id['message_id']
    message_remove(token1, message_id)
    message_dict = messages(token2, channel_id2, 0)
    assert message_dict['messages'] == []

#Tests for message_edit

def test_edit_accesserror():
    '''if user editing message did not create it and is not owner of channel nor flockr'''
    _, token1, _, token2, channel_id = setup()
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    with pytest.raises(AccessError):
        message_edit(token2, message_id, "hello")

def test_edit_invalidtoken():
    '''when token is invalid'''
    _, token1, _, _, channel_id = setup()
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    with pytest.raises(AccessError):
        message_edit('invalid_token', message_id, "hello")

def test_edit_invalid_mid():
    '''when message id is invalid'''
    _, token1, _, _, _ = setup()
    with pytest.raises(AccessError):
        message_edit(token1, 9, "hello")

def test_edit_deleted_message():
    '''when message has been deleted'''
    _, token, _, _, channel_id = setup()
    m_id = message_send(token, channel_id, "hewo")
    message_id = m_id['message_id']
    message_remove(token, message_id)
    with pytest.raises(AccessError):
        message_edit(token, message_id, "hello")

def test_edit_success():
    '''testing if user editing their message is successful'''
    _, token1, _, _, channel_id = setup()
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    message_edit(token1, message_id, "hello")
    m_dict = messages(token1, channel_id, 0)
    assert m_dict['messages'][0]['message'] == "hello"

def test_edit_emptystring():
    '''testing if editing empty string deletes string'''
    _, token1, _, _, channel_id = setup()
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    message_edit(token1, message_id, "")
    m_dict = messages(token1, channel_id, 0)
    assert m_dict['messages'] == []

def test_edit_multiple():
    '''testing if multiple messages can be removed'''
    _, token1, _, token2, channel_id = setup()
    join(token2, channel_id)
    message_send(token1, channel_id, "hi")
    m_id2 = message_send(token2, channel_id, "hey")
    message_send(token1, channel_id, "how are you")
    m_id4 = message_send(token2, channel_id, "fine thanks")
    message_id2 = m_id2['message_id']
    message_id4 = m_id4['message_id']
    message_edit(token2, message_id2, "hewo")
    message_edit(token2, message_id4, "great :D")
    m_dict = messages(token1, channel_id, 0)
    assert m_dict['messages'][2]['message'] == "hewo"
    assert m_dict['messages'][0]['message'] == "great :D"

def test_edit_by_channel_owner():
    '''testing if a channel owner can edit any message'''
    _, token1, u_id2, token2, channel_id = setup()
    addowner(token1, channel_id, u_id2)
    m_id = message_send(token1, channel_id, "hewo")
    message_id = m_id['message_id']
    message_edit(token2, message_id, "hello")
    m_dict = messages(token1, channel_id, 0)
    assert m_dict['messages'][0]['message'] == "hello"

def test_edit_by_flockr_owner():
    '''testing if flockr owner can edit any message'''
    _, token1, _, token2, _ = setup()
    ch_id2 = channels_create(token2, 'Angy', True)
    channel_id2 = ch_id2['channel_id']
    m_id = message_send(token2, channel_id2, "beepboop")
    message_id = m_id['message_id']
    message_edit(token1, message_id, "hello")
    m_dict = messages(token2, channel_id2, 0)
    assert m_dict['messages'][0]['message'] == "hello"

#Tests for message_sendlater

def test_sendlater_input_error1():
    '''input error when text over 1000 characters'''
    _, token, _, _, channel_id = setup()
    message = 'x'
    for i in range(1000):
        message += str(i)
    with pytest.raises(InputError):
        message_sendlater(token, channel_id, message, int(time.time()))

def test_sendlater_input_error2():
    '''input error when invalid channel_id'''
    _, token, _, _, _ = setup()
    message = 'x'
    with pytest.raises(InputError):
        message_sendlater(token, 10000, message, int(time.time()))

def test_sendlater_input_error3():
    '''input error time is in the past'''
    _, token, _, _, channel_id = setup()
    message = 'x'
    with pytest.raises(InputError):
        message_sendlater(token, channel_id, message, int(time.time()) - 10000)

def test_sendlater_access_error1():
    '''access error when invalid token'''
    _, _, _, _, ch_id = setup()
    token = 'notvalid'
    with pytest.raises(AccessError):
        message_sendlater(token, ch_id, 'x', int(time.time()) + 10)

def test_sendlater_access_error2():
    '''access error when user is not in the channel'''
    _, _, _, token, channel_id = setup()
    message = 'x'
    with pytest.raises(AccessError):
        message_sendlater(token, channel_id, message, int(time.time()) + 10)

def test_sendlater_single_success():
    '''successfuly sends a message at required time'''
    _, token, _, _, channel_id = setup()
    message = 'x'
    later_time = int(time.time()) + 1
    message_sendlater(token, channel_id, message, later_time)
    #assert message hasn't been sent
    m_dict = messages(token, channel_id, 0)
    assert m_dict['messages'] == []
    #wait for message to be sent
    time.sleep(1)
    #assert message has been sent at specific time
    m_dict = messages(token, channel_id, 0)
    assert m_dict['messages'][0]['time_created'] == later_time

def test_sendlater_multiple_success():
    '''successfuly sends lots of messages at different times'''
    _, token, _, _, channel_id = setup()
    m_one = 'i'
    m_two = 'love'
    m_three = 'u'
    time_one = int(time.time())
    time_two = int(time.time()) + 5
    time_three = int(time.time()) + 10
    message_sendlater(token, channel_id, m_three, time_three)
    message_send(token, channel_id, m_one)
    message_sendlater(token, channel_id, m_two, time_two)
    #assert only one message has been sent
    m_dict = messages(token, channel_id, 0)
    assert len(m_dict['messages']) == 1
    #wait for other messages to be sent
    time.sleep(10)
    #assert all three have been sent in right order
    m_dict = messages(token, channel_id, 0)
    assert m_dict['messages'][0]['time_created'] == time_three
    assert m_dict['messages'][1]['time_created'] == time_two
    assert m_dict['messages'][2]['time_created'] == time_one

#Tests for message_pin

def test_pin_input_error1():
    '''input error when message_id is invalid'''
    _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        message_pin(token1, -1)

def test_pin_input_error2():
    '''input error when message already pinned'''
    _, token1, _, _, ch_id = setup()
    message_id = message_send(token1, ch_id, 'hello')
    message_pin(token1, message_id['message_id'])
    with pytest.raises(InputError):
        message_pin(token1, message_id['message_id'])

def test_pin_access_error1():
    '''access error when user not part of channel'''
    _, token1, _, token2, ch_id = setup()
    message_id = message_send(token1, ch_id, 'hello')
    with pytest.raises(AccessError):
        message_pin(token2, message_id['message_id'])

def test_pin_access_error2():
    '''access error when user not owner of channel'''
    _, token1, _, token2, ch_id = setup()
    join(token2, ch_id)
    message_id = message_send(token1, ch_id, 'hello')
    with pytest.raises(AccessError):
        message_pin(token2, message_id['message_id'])

def test_pin_access_error3():
    '''access error when token is invalid'''
    _, token1, _, _, ch_id = setup()
    message_id = message_send(token1, ch_id, 'hello')
    with pytest.raises(AccessError):
        message_pin('invalid_token', message_id['message_id'])

def test_pin_success():
    '''confirms message was successfully pinned'''
    _, token1, _, _, ch_id = setup()
    message_id = message_send(token1, ch_id, 'hello')
    message_pin(token1, message_id['message_id'])
    m_dict = messages(token1, ch_id, 0)
    assert m_dict['messages'][0]['is_pinned'] == True

#Tests for message_unpin

def test_unpin_input_error1():
    '''input error when message_id is invalid'''
    _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        message_unpin(token1, -1)

def test_unpin_input_error2():
    '''input error when message already unpinned'''
    _, token1, _, _, ch_id = setup()
    message_id = message_send(token1, ch_id, 'hello')
    with pytest.raises(InputError):
        message_unpin(token1, message_id['message_id'])

def test_unpin_access_error1():
    '''access error when user not part of channel'''
    _, token1, _, token2, ch_id = setup()
    message_id = message_send(token1, ch_id, 'hello')
    message_pin(token1, message_id['message_id'])
    with pytest.raises(AccessError):
        message_unpin(token2, message_id['message_id'])

def test_unpin_access_error2():
    '''access error when user not owner of channel'''
    _, token1, _, token2, ch_id = setup()
    join(token2, ch_id)
    message_id = message_send(token1, ch_id, 'hello')
    message_pin(token1, message_id['message_id'])
    with pytest.raises(AccessError):
        message_unpin(token2, message_id['message_id'])

def test_unpin_access_error3():
    '''access error when token is invalid'''
    _, token1, _, _, ch_id = setup()
    message_id = message_send(token1, ch_id, 'hello')
    message_pin(token1, message_id['message_id'])
    with pytest.raises(AccessError):
        message_unpin('invalid_token', message_id['message_id'])

def test_unpin_success():
    '''confirms message was successfully unpinned'''
    _, token1, _, _, ch_id = setup()
    message_id = message_send(token1, ch_id, 'hello')
    message_pin(token1, message_id['message_id'])
    message_unpin(token1, message_id['message_id'])
    m_dict = messages(token1, ch_id, 0)
    assert m_dict['messages'][0]['is_pinned'] == False

#Tests for message_react

def test_react_empty_mid():
    '''input error when message id is empty'''
    _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        message_react(token1, '', 1)

def test_react_invalid_mid():
    '''input error when message id is invalid'''
    _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        message_react(token1, 99, 1)

def test_react_invalid_reactid():
    '''input error when react id is invalid'''
    _, token1, _, _, ch_id = setup()
    m_id = message_send(token1, ch_id, "hewo")
    message_id = m_id['message_id']
    with pytest.raises(InputError):
        message_react(token1, message_id, 99)

def test_react_already_reacted():
    '''input error when user tries to react 
    to a message they already reacted to'''
    _, token1, _, _, ch_id = setup()
    m_id = message_send(token1, ch_id, "hewo")
    message_id = m_id['message_id']
    message_react(token1, message_id, 1)
    with pytest.raises(InputError):
        message_react(token1, message_id, 1)

def test_react_not_in_channel():
    '''input error when user is not the channel of the message'''
    _, token1, _, token2, ch_id = setup()
    m_id = message_send(token1, ch_id, "hewo")
    message_id = m_id['message_id']
    with pytest.raises(InputError):
        message_react(token2, message_id, 1)

def test_react_invalid_token():
    '''access error when token is invalid'''
    _, token, _, _, ch_id = setup()
    m_id = message_send(token, ch_id, "hewo")
    message_id = m_id['message_id']
    with pytest.raises(AccessError):
        message_react('invalid_token', message_id, 1)

def test_react_own():
    '''user successfully thumbs up their own message'''
    u_id, token, _, _, ch_id = setup()
    m_id = message_send(token, ch_id, "hewo")
    message_id = m_id['message_id']
    message_react(token, message_id, 1)
    #check channel messages-reacts
    m_dict = messages(token, ch_id, 0)
    reacts_dict = m_dict['messages'][0]['reacts']
    assert reacts_dict == [{
        'react_id': 1,
        'u_ids': [u_id],
        'is_this_user_reacted': True
    }]

def test_react_other():
    '''user reacting to someone else's message'''
    #check channel messages-reacts
    _, token1, u_id2, token2, ch_id = setup()
    join(token2, ch_id)
    m_id = message_send(token1, ch_id, "hewo")
    message_id = m_id['message_id']
    message_react(token2, message_id, 1)

    m_dict1 = messages(token1, ch_id, 0)
    reacts_dict1 = m_dict1['messages'][0]['reacts']
    assert reacts_dict1 == [{
        'react_id': 1,
        'u_ids': [u_id2],
        'is_this_user_reacted': False
    }]

    m_dict2 = messages(token2, ch_id, 0)
    reacts_dict2 = m_dict2['messages'][0]['reacts']
    assert reacts_dict2 == [{
        'react_id': 1,
        'u_ids': [u_id2],
        'is_this_user_reacted': True
    }]

def test_react_multiple():
    '''more than one person reacting to messages'''
    #check channel messages-reacts
    u_id1, token1, _, token2, ch_id = setup()
    u_dict = auth_register('kaydensmith@gmail.com', 'k4yd3nsm1th', \
    'Kayden', 'Smith')
    u_id3, token3 = u_dict['u_id'], u_dict['token']
    join(token2, ch_id)
    join(token3, ch_id)
    m_id1 = message_send(token2, ch_id, "hewo")
    message_send(token3, ch_id, "hey")
    message_react(token3, m_id1['message_id'], 1)
    message_react(token1, m_id1['message_id'], 1)
    m_dict1 = messages(token1, ch_id, 0)
    reacts_dict1 = m_dict1['messages'][1]['reacts']
    assert reacts_dict1 == [{
        'react_id': 1,
        'u_ids': [u_id3, u_id1],
        'is_this_user_reacted': True 
    }]
    m_dict2 = messages(token2, ch_id, 0)
    reacts_dict2 = m_dict2['messages'][1]['reacts'] #hewo message
    assert reacts_dict2 == [{
        'react_id': 1,
        'u_ids': [u_id3, u_id1],
        'is_this_user_reacted': False
    }]


#Tests for message_unreact

def test_unreact_empty_mid():
    '''input error when message id is empty'''
    _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        message_unreact(token1, '', 1)

def test_unreact_invalid_mid():
    '''input error when message id is invalid'''
    _, token1, _, _, _ = setup()
    with pytest.raises(InputError):
        message_unreact(token1, 99, 1)

def test_unreact_invalid_reactid():
    '''input error when react id is invalid'''
    _, token1, _, _, ch_id = setup()
    m_id = message_send(token1, ch_id, "hewo")
    message_id = m_id['message_id']
    message_react(token1, message_id, 1)
    with pytest.raises(InputError):
        message_unreact(token1, message_id, 9)

def test_unreact_no_reacts():
    '''input error when message has no reacts'''
    _, token1, _, _, ch_id = setup()
    m_id = message_send(token1, ch_id, "hewo")
    message_id = m_id['message_id']
    with pytest.raises(InputError):
        message_unreact(token1, message_id, 1)

def test_unreact_not_reacted():
    '''input error when user tries to unreact
    to a message that they didn't react to'''
    _, token1, _, token2, ch_id = setup()
    join(token2, ch_id)
    m_id = message_send(token1, ch_id, "hewo")
    message_id = m_id['message_id']
    message_react(token1, message_id, 1)
    with pytest.raises(InputError):
        message_unreact(token2, message_id, 1)

def test_unreact_not_in_channel():
    '''input error when user is not the channel of the message'''
    _, token1, _, token2, ch_id = setup()
    m_id = message_send(token1, ch_id, "hewo")
    message_id = m_id['message_id']
    message_react(token1, message_id, 1)
    with pytest.raises(InputError):
        message_unreact(token2, message_id, 1)

def test_unreact_invalid_token():
    '''access error when token is invalid'''
    _, token, _, _, ch_id = setup()
    m_id = message_send(token, ch_id, "hewo")
    message_id = m_id['message_id']
    message_react(token, message_id, 1)
    with pytest.raises(AccessError):
        message_unreact('invalid_token', message_id, 1)

def test_unreact_success():
    '''user unreacting to their own message'''
    _, token1, _, _, ch_id = setup()
    m_id = message_send(token1, ch_id, "hewo")
    message_id = m_id['message_id']
    message_react(token1, message_id, 1)
    message_unreact(token1, message_id, 1)
    m_dict = messages(token1, ch_id, 0)
    reacts_dict = m_dict['messages'][0]['reacts']
    assert reacts_dict == []

def test_unreact_multiple():
    '''multiple users reacting to a message then
    one user unreacts'''
    _, token1, u_id2, token2, ch_id = setup()
    u_dict = auth_register('kaydensmith@gmail.com', 'k4yd3nsm1th', \
    'Kayden', 'Smith')
    u_id3, token3 = u_dict['u_id'], u_dict['token']
    join(token2, ch_id)
    join(token3, ch_id)
    m_id = message_send(token2, ch_id, "hewo")
    message_react(token3, m_id['message_id'], 1)
    message_react(token1, m_id['message_id'], 1)
    message_react(token2, m_id['message_id'], 1)
    message_unreact(token1, m_id['message_id'], 1)
    m_dict1 = messages(token1, ch_id, 0)
    reacts_dict1 = m_dict1['messages'][0]['reacts']
    assert reacts_dict1 == [{
        'react_id': 1,
        'u_ids': [u_id3, u_id2],
        'is_this_user_reacted': False
    }]
    message_unreact(token3, m_id['message_id'], 1)
    m_dict2 = messages(token2, ch_id, 0)
    reacts_dict2 = m_dict2['messages'][0]['reacts']
    assert reacts_dict2 == [{
        'react_id': 1,
        'u_ids': [u_id2],
        'is_this_user_reacted': True
    }]
