'''
User Functions
'''
from error import InputError, AccessError
from db import db
from auth import decode_token, check_email, check_name, check_handle
from helper_functions import token_validation, get_u_id
from PIL import Image
from flask import request
import imgspy
import pathlib
import os
import requests
import urllib.request

def update_user_obj(token, u_id, key, value):
    """
    Helper Function to get user obj.
    """
    for account in db['accounts'].values():
        if account['token'] == token and account['u_id'] == u_id:
            account[key] = value
            break
    else:
        raise AccessError(description="Account not found")

def user_profile(token, u_id):
    """
    Retrieve User Profile
    """
    if not token_validation(token):
        raise AccessError(description="Invalid Token")

    for account in db['accounts'].values():
        if account['u_id'] == u_id:
            return {
                'user': {
                    'u_id': account['u_id'],
                    'email': account['email'],
                    'name_first': account['name_first'],
                    'name_last': account['name_last'],
                    'handle_str': account['handle_str'],
                    'profile_img_url': account['profile_img_url'] if account['profile_img_url'] is not None else "",
                }
            }
    raise AccessError(description=f"Account not found.")

def user_profile_setname(token, name_first, name_last):
    """
    Set f/l name of user
    """

    u_id = decode_token(token)
    if not check_name(name_first):
        raise InputError(description="Invalid First Name")
    if not check_name(name_last):
        raise InputError(description="Invalid Last Name")
    update_user_obj(token, u_id, 'name_first', name_first)
    update_user_obj(token, u_id, 'name_last', name_last)
    return {}

def user_profile_setemail(token, email):
    """
    Set email of user
    """

    u_id = decode_token(token)
    if not check_email(email):
        raise InputError(description="Invalid Email.")
    update_user_obj(token, u_id, 'email', email)
    return {}

def user_profile_sethandle(token, handle_str):
    """
    Set handle of user
    """

    u_id = decode_token(token)
    if not check_handle(handle_str):
        raise InputError(description="Invalid Handle.")
    update_user_obj(token, u_id, 'handle_str', handle_str)
    return {}

def user_upload_photo(token, img_url, x_start, y_start, x_end, y_end):

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
    update_user_obj(token, u_id, 'profile_img_url', url)
    
    return {}
