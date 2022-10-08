'''
User Functions
'''
from error import InputError, AccessError
from db import get_db
from auth import check_email, check_name, check_handle
from helper_functions import token_validation, get_u_id
from PIL import Image
from flask import request
import imgspy
import pathlib
import os
import requests
import urllib.request

db = get_db()

def user_profile(token, u_id):
    """
    Retrieve User Profile
    """
    if not token_validation(token):
        raise AccessError(description="Invalid Token")
    
    with db.cursor() as cur:
        cur.execute("select * from users where id = %s", [u_id])
        
        if cur.rowcount == 0:
            raise AccessError(description=f"Account not found.")
        
        user = cur.fetchone()
        
        return {
            'user': {
                'u_id': user[0],
                'email': user[1],
                'name_first': user[3],
                'name_last': user[4],
                'handle_str': user[5],
                'profile_img_url': user[6],
            }
        }
    

def user_profile_setname(token, name_first, name_last):
    """
    Set f/l name of user
    """
    if not token_validation(token):
        raise AccessError(description="Invalid Token")
    
    u_id = get_u_id(token)
    
    if not check_name(name_first):
        raise InputError(description="Invalid First Name")
    
    if not check_name(name_last):
        raise InputError(description="Invalid Last Name")
    
    with db.cursor() as cur:
        cur.execute("update users set first_name = %s, last_name = %s where id = %s", [name_first, name_last, u_id])
    
    return {}

def user_profile_setemail(token, email):
    """
    Set email of user
    """
    if not token_validation(token):
        raise AccessError(description="Invalid Token")
    
    u_id = get_u_id(token)
    
    if not check_email(email):
        raise InputError(description="Invalid Email.")
    
    with db.cursor() as cur:
        cur.execute("update users set email = %s where id = %s", [email, u_id])
    
    return {}

def user_profile_sethandle(token, handle_str):
    """
    Set handle of user
    """
    if not token_validation(token):
        raise AccessError(description="Invalid Token")
    
    u_id = get_u_id(token)
    
    if not check_handle(handle_str):
        raise InputError(description="Invalid Handle.")
    
    with db.cursor() as cur:
        cur.execute("update users set handle = %s where id = %s", [handle_str, u_id])
        
    return {}

def user_upload_photo(token, img_url, x_start, y_start, x_end, y_end):
    if not token_validation(token):
        raise AccessError(description="Invalid Token")
    
    if x_start >= x_end or y_start >= y_end:
        raise InputError(description= 'Crop dimensions are invalid')

    # Url status code is not 200
    if requests.get(img_url).status_code != 200:
        raise InputError(description = 'HTTP status code is invalid')
    
    try:
        img_dict = imgspy.info(img_url)
    except:
        raise InputError(description = 'HTTP status code is invalid')

    width = img_dict['width'] 
    height = img_dict['height']

    # Image is not a .jpg 
    if img_dict['type'] != 'jpg':
        raise InputError(description = 'Image is not a jpg')
    
    # Image is out of dimensions 
    if (int(x_start) or int(x_end) not in range(width)) or (int(y_start) or int(y_end) not in range(height)):
        raise InputError(description='Crop coordinates are out of dimensions of image')

    u_id = get_u_id(token)

    # Check if user_accounts_imgs exists, if not create folder
    if not os.path.exists(os.path.join(pathlib.Path(__file__).parent, 'user_account_imgs')):
        os.makedirs(os.path.join(pathlib.Path(__file__).parent, 'user_account_imgs'))

    # Creating the path for the image from the url
    img_path = os.path.join(pathlib.Path(__file__).parent, 'user_account_imgs', f'{u_id}.jpg')
 
    # Image download
    _, _ = urllib.request.urlretrieve(img_url, img_path)

    # Image cropping
    img = Image.open(img_path)
    cropped = img.crop((int(x_start), int(y_start), int(x_end), int(y_end)))
    cropped.save(img_path)

    url = request.url_root + '/user_account_imgs' + f"/{u_id}.jpg"
    
    with db.cursor() as cur:
        cur.execute("update users set profile_img = %s where id = %s", [url, u_id])
    
    return {}
