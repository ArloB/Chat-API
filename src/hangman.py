'''
Hangman
'''
import random
import os
from string import ascii_lowercase
from db import db
from error import InputError
from message import message_send

HANGMANPICS = ['''
  +---+
  |   |
      |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========''']

def hangman_start(token, channel_id):
    '''
    Starts Hangman Game
    '''
    words = []
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f'{dir_path}/hard_hangman_words.txt', 'r') as f:
        for word in f:
            words.append(word.strip())
    selected_word = random.choice(words).lower()
    current = '*' * len(selected_word)
    channel = db['channels'].get(channel_id, None)
    if channel is None:
        raise InputError(description="Invalid Channel Id")
    channel['hangman'] = {
        'guesses': list(),
        'word': selected_word,
        'current': current,
        'fails': 0,
        'max_fails': 6,
        'token': token
    }
    # Sending Messages to channel
    message = f"A hangman game has been started.{HANGMANPICS[0]}\n{current}"
    message_send(token, channel_id, message)
    return channel['hangman']

def hangman_guess(letter, channel_id):
    '''
    Guess letter with hangman
    '''
    # Getting Hangman Obj
    channel = db['channels'].get(channel_id, None)
    if channel is None:
        raise InputError(description="Invalid Channel Id")
    hangman_obj = channel.get('hangman', None)
    if hangman_obj is None:
        raise InputError(description="No ongoing Hangman game")
    # Verifying Letter is Valid
    letter = letter.lower()
    if letter not in ascii_lowercase:
        raise InputError(description=f"Character {letter} is not valid")
    if letter in hangman_obj['guesses']:
        raise InputError(description=f"Letter {letter} has already been chosen")
    if hangman_obj['current'] == hangman_obj['word']:
        raise InputError(description="Game is already over. Start a new game.")
    # Adding letter to guesses
    hangman_obj['guesses'].append(letter)
    guesses = hangman_obj['guesses']
    word = hangman_obj['word']
    current = hangman_obj['current']
    token = hangman_obj['token']
    if letter in word:
        # Updating Current
        current = hangman_obj['current'] = construct_current(word, hangman_obj['guesses'])
        guesses_left = hangman_obj['max_fails'] - hangman_obj['fails']
        game_win = current == word
        game_state = {
            'current': current,
            'guesses': guesses,
            'guesses_left': guesses_left,
            'state': 'Correct'
        }
        # Sending messages to channel
        if game_win:
            game_win_messages(current, hangman_obj['max_fails'] - hangman_obj['fails'], token, channel_id)
            # Ending Hangman Game
            channel.pop('hangman')
        else:
            game_correct_guess_messages(current, guesses_left, guesses, token, channel_id)
    else:
        # Returning Response and updating
        hangman_obj['fails'] += 1
        guesses_left = hangman_obj['max_fails'] - hangman_obj['fails']
        game_over = hangman_obj['fails'] == hangman_obj['max_fails']
        game_state = {
            'current': current,
            'guesses': guesses,
            'guesses_left': guesses_left,
            'state': 'Incorrect'
        }
        # Sending messages to channel
        if game_over:
            game_over_messages(word, token, channel_id)
            # Ending Hangman Game
            channel.pop('hangman')
        else:
            game_incorrect_guess_messages(current, guesses_left, guesses, token, channel_id)
    return game_state

def construct_current(actual_word, guesses):
    '''
    Creating current state from * and chars
    '''
    current = ""
    for char in actual_word:
        if char in guesses:
            current += char
        else:
            current += '*'
    return current

def game_correct_guess_messages(current, guesses_left, guesses, token, channel_id):
    '''
    Correct Guess
    '''
    message = f"You guessed was correct.{HANGMANPICS[-guesses_left-1]}\n{current}, following letters guessed: {', '.join(guesses)}"
    message_send(token, channel_id, message)

def game_incorrect_guess_messages(current, guesses_left, guesses, token, channel_id):
    '''
    Incorrect Guess
    '''
    message = f"Your guess was incorrect.{HANGMANPICS[-guesses_left-1]}\n{current}, following letters guessed: {', '.join(guesses)}"
    message_send(token, channel_id, message)

def game_win_messages(current, guesses_left, token, channel_id):
    '''
    Game win
    '''
    message = f"You correctly guessed the word! The word was {current}.{HANGMANPICS[-guesses_left-1]}"
    message_send(token, channel_id, message)

def game_over_messages(word, token, channel_id):
    '''
    Game over
    '''
    message = f"Game over. The correct word was actually {word}.{HANGMANPICS[-1]}"
    message_send(token, channel_id, message)
