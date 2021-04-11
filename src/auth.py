'''
Auth Functions
'''
import hashlib
import time
import re
import random
import jwt
from db import db
from error import InputError
from email.message import EmailMessage
import smtplib

EMAIL_REGEX = r'^[a-z0-9]+[\._]?[a-z0-9]*[@]\w+[.]\w{2,3}$'

def check_email(email):
    '''
    Checks if email is valid
    '''
    return bool(re.search(EMAIL_REGEX, email)) # Returns true or false depending on match

def create_handle(name_first, name_last):
    '''
    Creates Handle for user. Unique Handle for each user.
    '''
    handle = name_last.lower()[0] + name_first.lower() # "Jason Yu -> yjason123"
    if not check_handle(handle):
        handle = handle[:20]
    handles = set()
    for account in db['accounts'].values():
        handles.add(account.get('handle', None))
    while handle in handles: # Handle is taken
        if len(handle) == 20:
            handle[random.randint(0, 19)] = str(random.randint(1, 9))
        else:
            handle += str(random.randint(1, 9))
    return handle

def check_handle(handle):
    '''
    Check if Handle is valid length
    '''
    return 3 <= len(handle) <= 20

def check_password(password):
    '''
    Check if Password is valid length
    '''
    return len(password) >= 6

def check_name(name):
    '''
    Check if Name is valid length
    '''
    return 1 <= len(name) <= 50

def new_token(u_id):
    '''
    Token is based on time that user logged in and existing user id
    Computation Time between calls + u_id should eliminate possibility of duplicate tokens
    '''
    payload = {"u_id": u_id}
    token = jwt.encode(payload, 'secret', algorithm='HS512').decode("utf-8") 
    return token

def new_password_reset_code(email):
    '''
    Get reset code based off of email. All Reset codes are unique due to random.random()
    '''
    payload = {"email": email, "random": random.random()}
    reset_code = jwt.encode(payload, 'secret', algorithm='HS512').decode("utf-8") 
    return reset_code

def send_new_password_reset_code(email):
    '''
    Send email to account containing reset code
    '''
    reset_code = new_password_reset_code(email)
    # Create Email Message
    msg = EmailMessage()
    msg.set_content(f"Reset Code: {reset_code}")
    msg['Subject'] = 'Flockr Verification Code'
    msg['From'] = 'testingemailfor1531project@gmail.com'
    msg['To'] = email
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('testingemailfor1531project@gmail.com', 'abcABC123987')
    s.send_message(msg)
    s.quit()
    return reset_code

def decode_password_reset_code(reset_code):
    '''
    Extracts u_id and login time
    '''
    obj = jwt.decode(reset_code, 'secret', algorithms=['HS512'])
    email = obj.get('email')
    if email == None:
        raise InputError(description="Invalid Reset Code")
    return email

def decode_token(token):
    '''
    Extracts u_id and login time
    '''
    u_id = jwt.decode(token, 'secret', algorithms=['HS512'])["u_id"]
    return int(u_id)

def new_u_id():
    '''
    U_ID is based on time that user registers
    Computation Time between calls should eliminate possibility of duplicate tokens
    '''
    return len(db['accounts']) + 1

def auth_login(email, password):
    '''
    Logins user. New token is assigned to account and u_id, token returned.
    '''
    password = hashlib.sha256(password.encode()).hexdigest()

    account = db['accounts'].get(email, None)
    if account is None:
        raise InputError("Account does not exist.")
    if not check_email(email):
        raise InputError(description="Email is not valid.")
    if password != account['password']:
        raise InputError(description="Password is incorrect.")
    u_id = account['u_id']
    token = account['token'] = new_token(u_id)
    return {
        'u_id': u_id,
        'token': token,
    }

def auth_logout(token):
    '''
    Logouts user corresponding to given token. Token is then set to None.
    '''
    for account in db['accounts'].values():
        if account['token'] == token:
            account['token'] = None # Resetting Token
            return {
                'is_success': True,
            }
    return {
        'is_success': False
    }

def auth_register(email, password, name_first, name_last):
    '''
    Registers User to the databse.
    '''
    found = db['accounts'].get(email)
    first_user = len(db['accounts']) == 0
    if not check_email(email):
        raise InputError(description="Email is not valid.")
    if not check_name(name_first):
        raise InputError(description=f"First name is not valid {name_first}")
    if not check_name(name_last):
        raise InputError(description=f"Last name is not valid {name_last}")
    if not check_password(password):
        raise InputError(description="Password is not valid.")
    if found != None:
        raise InputError(description="Email has already been taken.")
    u_id = new_u_id()
    token = new_token(u_id)
    db['accounts'][email] = {
        'u_id': u_id,
        'email': email,
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': create_handle(name_first, name_last),
        'token': token,
        'is_owner': first_user, # True on First User
        'profile_img_url': None
    }
    return {
        'u_id': u_id,
        'token': token,
    }

def auth_password_reset_request(email):
    '''
    Request for password reset
    '''
    account = db['accounts'].get(email, None)
    if account is None:
        raise InputError(description="Account does not exist")
    if not check_email(email):
        raise InputError(description="Email is invalid")
    # Updating Reset Code
    account['reset_code'] = send_new_password_reset_code(email)
    return {}

def auth_password_reset(reset_code, new_password):
    """
    Reset Password with reset code
    """
    if not check_password(new_password):
        raise InputError(description="New password is not valid.")
    try:
        email = decode_password_reset_code(reset_code)
        account = db['accounts'].get(email, None)
        # Checking decode email is equal to account email
        assert account['email'] == email
        account['password'] = hashlib.sha256(new_password.encode()).hexdigest()
    except:
        raise InputError(description="Reset Code is invalid.")
    return {}

