'''
Auth Functions
'''
from datetime import datetime
import hashlib
import re
import random
import jwt
import psycopg2
from db import get_db
from error import InputError
from email.message import EmailMessage
import smtplib
from helper_functions import decode_token

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

db = get_db()

def check_email(email):
    '''
    Checks if email is valid
    '''
    return EMAIL_REGEX.match(email) # Returns true or false depending on match

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

def new_token(u_id, iat):
    '''
    Token is based on time that user logged in and existing user id
    Computation Time between calls + u_id should eliminate possibility of duplicate tokens
    '''
    payload = {"u_id": u_id, "iat": iat}
    token = jwt.encode(payload, 'secret', algorithm='HS512')
    return token

def new_password_reset_code(email):
    '''
    Get reset code based off of email. All Reset codes are unique due to random.random()
    '''
    payload = {"email": email, "random": random.random()}
    reset_code = jwt.encode(payload, 'secret', algorithm='HS512')
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

def auth_login(email, password):
    '''
    Logins user. New token is assigned to account and u_id, token returned.
    '''
    password = hashlib.sha256(password.encode()).hexdigest()
    
    if not check_email(email):
        raise InputError(description="Email is not valid.")
    
    iat = int(datetime.now().timestamp())
    
    with db.cursor() as cur:
        cur.execute("select id, password from users where email = %s", [email])
        
        account = cur.fetchone()
        
        if account is None:
            raise InputError("Account does not exist.")
        
        if password != account[1]:
            raise InputError(description="Password is incorrect.")
        
        u_id = account[0]
        
        cur.execute("update users set iat = %s where id = %s", [iat, u_id])
            
    return {
        'u_id': u_id,
        'token': new_token(u_id, iat)
    }

def auth_logout(token):
    '''
    Logouts user corresponding to given token. Token is then set to None.
    '''
    u_id, iat = decode_token(token)
    
    success = False
    
    if u_id is not None and int(iat) != 0:
        try:
            with db.cursor() as cur:
                cur.execute("update users set iat = %s where id = %s", [0, u_id])
            
            success = True
        except:
            pass
    
    return {
        "is_success": success
    }

def auth_register(email, password, name_first, name_last):
    '''
    Registers User to the databse.
    '''
    if not check_email(email):
        raise InputError(description="Email is not valid.")
    if not check_name(name_first):
        raise InputError(description=f"First name is not valid {name_first}")
    if not check_name(name_last):
        raise InputError(description=f"Last name is not valid {name_last}")
    if not check_password(password):
        raise InputError(description="Password is not valid.")
    
    iat = int(datetime.now().timestamp())
    print(db)
    try:
        with db.cursor() as cur:
            cur.execute(""" insert into users (email, password, first_name, last_name, iat)
                            values (%s, %s, %s, %s, %s)
                            returning id""", [email, hashlib.sha256(password.encode()).hexdigest(), name_first, name_last, iat])
            u_id = cur.fetchone()[0]
    except psycopg2.Error as e:
        if int(e.pgcode) == 23505:
            raise InputError(description="Email has already been taken.")
        else:
            print(e)
            raise InputError(description=f"DB Error: {e.pgcode}")
    
    token = new_token(u_id, iat)

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

