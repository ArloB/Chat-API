'''
Testing hangman
'''
import pytest
from error import InputError
from other import clear
from hangman import hangman_start, hangman_guess
from auth import auth_register
from channels import channels_create

def register_default():
    '''
    Register Default User
    '''
    return auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

def test_start():
    '''
    Testing Valid Hangman Start
    '''
    clear()
    res = register_default()
    token = res['token']
    res = channels_create(token, "channel", True)
    channel_id = res['channel_id']
    res = hangman_start(token, channel_id)

def test_full_game():
    '''
    Test Full Game
    '''
    clear()
    res = register_default()
    token = res['token']
    res = channels_create(token, "channel", True)
    channel_id = res['channel_id']
    res = hangman_start(token, channel_id)
    for char in 'abcdefghijklmnopqrstuvwxyz':
        res = hangman_guess(char, channel_id)
        guesses_left = res['guesses_left']
        current = res['current']
        if guesses_left == 0: 
            break
        if '*' not in current:
            break


def test_invalid_start():
    '''
    Testing Invalid Hangman Start
    '''
    clear()
    res = register_default()
    token = res['token']
    with pytest.raises(InputError):
        res = hangman_start(token, None)

def test_guess():
    '''
    Valid Guess
    '''
    clear()
    res = register_default()
    token = res['token']
    res = channels_create(token, "channel", True)
    channel_id = res['channel_id']
    res = hangman_start(token, channel_id)
    res = hangman_guess('a', channel_id)

def test_guess_invalid():
    '''
    Testing for repeat character
    '''
    clear()
    res = register_default()
    token = res['token']
    res = channels_create(token, "channel", True)
    channel_id = res['channel_id']
    res = hangman_start(token, channel_id)
    res = hangman_guess('a', channel_id)
    with pytest.raises(InputError):
        res = hangman_guess('a', channel_id)

def test_guess_invalid_2():
    '''
    Testing for invalid character which is numeric
    '''
    clear()
    res = register_default()
    token = res['token']
    res = channels_create(token, "channel", True)
    channel_id = res['channel_id']
    res = hangman_start(token, channel_id)
    with pytest.raises(InputError):
        res = hangman_guess('9', channel_id)

def test_guess_invalid_3():
    '''
    Testing for guess on non running game
    '''
    clear()
    res = register_default()
    token = res['token']
    res = channels_create(token, "channel", True)
    channel_id = res['channel_id']
    with pytest.raises(InputError):
        res = hangman_guess('a', channel_id)