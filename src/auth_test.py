'''
Auth Tests
'''
import pytest
import auth
from error import InputError
from other import clear
from auth import new_password_reset_code

def register_default():
    return auth.auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

def test_register_than_login():
    '''
    Testing Register than Login.
    '''
    clear()
    register_default()
    # Expect to work since we registered
    result = auth.auth_login('validemail@gmail.com', '123abc!@#')
    # Expect to work since we've logged in
    assert auth.auth_logout(result['token'])['is_success'] is True

def test_register_same():
    '''
    Testing Register same account.
    '''
    clear()
    register_default()
    with pytest.raises(InputError):
        # Expect fail since registered already
        auth.auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')

def test_login_invalid_email():
    '''
    Testing Invalid Email.
    '''
    clear()
    register_default()
    with pytest.raises(InputError):
        # Expect fail since never registered
        auth.auth_login('didntusethis@gmail.com', '123abcd!@#')

def test_login_wrong_password():
    '''
    Testing Wrong Password.
    '''
    clear()
    register_default()
    with pytest.raises(InputError):
        # Expect to fail since we've never registered
        auth.auth_login('validemail@gmail.com', 'wrong password')

def test_logout_after_register():
    '''
    Testing Logging Out
    '''
    clear()
    result = register_default()
    # Expect to work since after registration
    assert auth.auth_logout(result['token'])['is_success'] is True

def test_logout_with_invalid():
    '''
    Testing Logging Out with invalid token
    '''
    clear()
    register_default()
    # Expect to fail since invalid token
    assert auth.auth_logout("InvalidToken")['is_success'] is False

def test_logout_twice():
    '''
    Testing Logging out twice with expired token.
    '''
    clear()
    result = register_default()
    # Expect to work since after registration
    assert auth.auth_logout(result['token'])['is_success'] is True
    # Expect to fail since after logout
    assert auth.auth_logout(result['token'])['is_success'] is False

def test_register_invalid_email():
    '''
    Testing Invalid Email
    '''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('', '123abc!@#', 'Hayden', 'Everest')

def test_register_invalid_name():
    '''
    Testing Register with invalid name
    '''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('validemail@gmail.com', '123abc!@#', '', '')

def test_register_invalid_password():
    '''
    Testing Register with invalid password
    '''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('validemail@gmail.com', 'abc', 'Hayden', 'Everest')

def test_password_reset_request():
    '''
    Testing Password Reset Request
    '''    
    clear()
    email = 'validemail@gmail.com'
    register_default()
    auth.auth_password_reset_request(email)

def test_password_reset():
    '''
    Testing Password Reset
    '''    
    clear()
    email = 'validemail@gmail.com'
    register_default()
    auth.auth_password_reset_request(email)
    auth.auth_password_reset(new_password_reset_code(email), "123abc!@#NEWPASSWORD")

