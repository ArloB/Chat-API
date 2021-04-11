'''
Auth HTTP Tests
'''
import requests
from other import clear
from auth import new_password_reset_code

DEFAULT_REGISTRATION_DATA = {
    "email": "validemail@gmail.com",
    "password": "123abc!@#",
    "name_first": "Hayden",
    "name_last": "Everest",
}

DEFAULT_LOGIN_DATA = {
    "email": "validemail@gmail.com",
    "password": "123abc!@#"
}

def register_default_user(url):
    '''
    Registers User. Remember to clear after testing is done to avoid unintended errors.
    '''
    url_register = url + 'auth/register'
    resp = requests.post(url_register, json=DEFAULT_REGISTRATION_DATA)
    result_body = resp.json()
    return result_body

def test_register_than_login(url):
    '''
    Testing Register than Login.
    '''
    clear()
    url_logout = url + 'auth/logout'
    url_login = url + 'auth/login'
    register_default_user(url)
    # Expect to succeed
    resp = requests.post(url_login, json=DEFAULT_LOGIN_DATA)
    result_body = resp.json()
    # Expect to Succeed
    logout_data = {
        'token': result_body['token'],
    }
    resp = requests.post(url_logout, json=logout_data)
    result_body = resp.json()
    assert resp.status_code == 200

def test_register_same(url):
    '''
    Testing Register same account.
    '''
    clear()
    url_register = url + 'auth/register'
    resp = requests.post(url_register, json=DEFAULT_REGISTRATION_DATA)
    resp = requests.post(url_register, json=DEFAULT_REGISTRATION_DATA)
    assert resp.status_code == 400

def test_login_invalid_email(url):
    '''
    Testing Invalid Email.
    '''
    clear()
    url_login = url + 'auth/login'
    register_default_user(url)
    # Expect login to fail since invalid email
    login_data = DEFAULT_LOGIN_DATA.copy()
    login_data['email'] = 'didntusethis@gmail.com'
    resp = requests.post(url_login, json=login_data)
    assert resp.status_code == 400

def test_login_wrong_password(url):
    '''
    Testing Wrong Password.
    '''
    clear()
    url_login = url + 'auth/login'
    register_default_user(url)
    # Expect login to fail since invalid password
    login_data = DEFAULT_LOGIN_DATA.copy()
    login_data['password'] = 'wrong password'
    resp = requests.post(url_login, json=login_data)
    assert resp.status_code == 400

def test_logout_after_register(url):
    '''
    Testing Logging Out
    '''
    clear()
    url_logout = url + 'auth/logout'
    result_body = register_default_user(url)
    # Expect to succeed since after registration
    logout_data = {
        'token': result_body['token']
    }
    resp = requests.post(url_logout, json=logout_data)
    assert resp.status_code == 200
    result_body = resp.json()
    assert result_body['is_success'] is True

def test_logout_with_invalid(url):
    '''
    Testing Logging Out with invalid token
    '''
    clear()
    url_logout = url + 'auth/logout'
    register_default_user(url)
    # Expect to fail since invalid token
    logout_data = {
        'token': 'InvalidToken'
    }
    resp = requests.post(url_logout, json=logout_data)
    assert resp.status_code == 200
    result_body = resp.json()
    assert result_body['is_success'] is False

def test_logout_twice(url):
    '''
    Testing Logging out twice with expired token.
    '''
    clear()
    url_logout = url + 'auth/logout'
    result_body = register_default_user(url)
    # Expect to work since after registration
    logout_data = {
        'token': result_body['token']
    }
    # Logging out should remove token
    resp = requests.post(url_logout, json=logout_data)
    assert resp.status_code == 200
    result_body = resp.json()
    assert result_body['is_success'] is True
    # Expect to fail since after logout
    resp = requests.post(url_logout, json=logout_data)
    assert resp.status_code == 200
    result_body = resp.json()
    assert result_body['is_success'] is False

def test_register_invalid_email(url):
    '''
    Testing Invalid Email
    '''
    clear()
    url_register = url + 'auth/register'
    registration_data = DEFAULT_REGISTRATION_DATA.copy()
    registration_data['email'] = ''
    resp = requests.post(url_register, json=registration_data)
    assert resp.status_code == 400

def test_register_invalid_name(url):
    '''
    Testing Register with invalid name
    '''
    clear()
    url_register = url + 'auth/register'
    registration_data = DEFAULT_REGISTRATION_DATA.copy()
    registration_data['name_first'] = ''
    registration_data['name_last'] = ''
    resp = requests.post(url_register, json=registration_data)
    assert resp.status_code == 400

def test_register_invalid_password(url):
    '''
    Testing Register with invalid password
    '''
    clear()
    url_register = url + 'auth/register'
    registration_data = DEFAULT_REGISTRATION_DATA.copy()
    registration_data['password'] = 'abc'
    resp = requests.post(url_register, json=registration_data)
    assert resp.status_code == 400

def test_password_reset_request(url):
    '''
    Testing Password Reset Request
    '''    
    clear()
    url_register = url + 'auth/register'
    url_password_reset_request = url + 'auth/passwordreset/request'
    # Registering Email
    registration_data = DEFAULT_REGISTRATION_DATA.copy()
    email = registration_data['email'] = 'validemail@gmail.com'
    resp = requests.post(url_register, json=registration_data)
    # Posting Reset Request
    req_data = {
        'email': email
    }
    resp = requests.post(url_password_reset_request, json=req_data)
    print(resp.json())
    assert resp.status_code == 200

def test_password_reset(url):
    '''
    Testing Password Reset
    '''    
    clear()
    url_password_reset = url + 'auth/passwordreset/reset'
    url_register = url + 'auth/register'
    # Registering Email
    registration_data = DEFAULT_REGISTRATION_DATA.copy()
    email = registration_data['email'] = 'validemail@gmail.com'
    requests.post(url_register, json=registration_data)
    # Posting Reset Request
    reset_data = {
        'new_password': "123abc!@#NEWPASSWORD",
        'reset_code': new_password_reset_code(email)
    }
    resp = requests.post(url_password_reset, json=reset_data)
    assert resp.status_code == 200

if __name__ == '__main__':
    test_password_reset_request("http://127.0.0.1:38243/")
