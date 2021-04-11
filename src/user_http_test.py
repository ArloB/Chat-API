'''
User Tests
'''
import requests
from other import clear

DEFAULT_REGISTRATION_DATA = {
    "email": "validemail@gmail.com",
    "password": "123abc!@#",
    "name_first": "Hayden",
    "name_last": "Everest"
}

USER_DATA1 = {
    'email': 'email@email.com',
    'password': 'password',
    'name_first': 'first',
    'name_last': 'last'
}

USER_DATA2 = {
    'email': 'other@gmail.com',
    'password': 'verystronk',
    'name_first': 'Jim',
    'name_last': 'Halpert'
}

def create_backend(url):
    clear()
    url_register = url + 'auth/register'

    resp = requests.post(url_register, json=USER_DATA1)
    user1 = resp.json()
    resp = requests.post(url_register, json=USER_DATA2)
    user2 = resp.json()

    return user1['u_id'], user1['token'], user2['u_id'], user2['token']

def register_default_user(url):
    '''
    Registers User. Remember to clear after testing is done to avoid unintended errors.
    '''
    url_register = url + 'auth/register'
    resp = requests.post(url_register, json=DEFAULT_REGISTRATION_DATA)
    result_body = resp.json()
    return result_body

def get_user_profile(url, token, u_id):
    '''
    Gets user profile in one easy function. Returns user dict
    '''
    profile_params = {
        'token': token, 'u_id': u_id
    }
    url_user_profile = url + 'user/profile'
    resp = requests.get(url_user_profile, params=profile_params)
    result_body = resp.json()
    return result_body['user']

def test_user_profile(url):
    '''
    Retrieving User Profile
    '''
    clear()
    url_user_profile = url + 'user/profile'
    result_body = register_default_user(url)
    token, u_id = result_body['token'], result_body['u_id']
    profile_params = {
        'token': token, 'u_id': u_id
    }
    resp = requests.get(url_user_profile, params=profile_params)
    assert resp.ok

def test_user_setname(url):
    '''
    Testing Set Name
    '''
    clear()
    url_user_setname = url + 'user/profile/setname'
    result_body = register_default_user(url)
    token, u_id = result_body['token'], result_body['u_id']
    setname_data = {
        'token': token, 'u_id': u_id, 'name_first': 'Jason', 'name_last': 'Yu'
    }
    requests.put(url_user_setname, json=setname_data)
    profile = get_user_profile(url, token, u_id)
    assert profile['name_first'] == 'Jason'
    assert profile['name_last'] == 'Yu'

def test_user_setemail(url):
    '''
    Testing Set Email
    '''
    clear()
    url_user_setemail = url + 'user/profile/setemail'
    result_body = register_default_user(url)
    token, u_id = result_body['token'], result_body['u_id']
    setemail_data = {
        'token': token, 'u_id': u_id, 'email': 'newtestemail@email.com'
    }
    requests.put(url_user_setemail, json=setemail_data)
    profile = get_user_profile(url, token, u_id)
    assert profile['email'] == 'newtestemail@email.com'

def test_user_sethandle(url):
    '''
    Testing Set Handle
    '''
    clear()
    url_user_sethandle = url + 'user/profile/sethandle'
    result_body = register_default_user(url)
    token, u_id = result_body['token'], result_body['u_id']
    sethandle_data = {
        'token': token, 'u_id': u_id, 'handle_str': 'jasonyuhandle'
    }
    requests.put(url_user_sethandle, json=sethandle_data)
    profile = get_user_profile(url, token, u_id)
    assert profile['handle_str'] == 'jasonyuhandle'

# User_uploadphoto HTTP tests

def test_uploadphoto_invalid_HTTP_status(url):
    _, token, _, _ = create_backend(url)

    url_upload_photo = url + 'user/profile/uploadphoto'

    img_data = {
        'token': token,
        'img_url': 'http://google.com/404',
        'x_start': 0,
        'y_start': 0,
        'x_end': 34,
        'y_end': 34
    }

    assert requests.post(url_upload_photo, json=img_data).status_code == 400

def test_uploadphoto_not_jpg(url):
    _, token, _, _ = create_backend(url)

    url_upload_photo = url + 'user/profile/uploadphoto'

    img_data1 = {
        'token': token,
        'img_url': 'https://www.arlo.com/images/Arlov4/home/product-j-1--a.png',
        'x_start': 0,
        'y_start': 0,
        'x_end': 34,
        'y_end': 34        
    }

    img_data2 = {
        'token': token,
        'img_url': 'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png',
        'x_start': 0,
        'y_start': 0,
        'x_end': 34,
        'y_end': 34          
    }

    assert requests.post(url_upload_photo, json=img_data1).status_code == 400
    assert requests.post(url_upload_photo, json=img_data2).status_code == 400



def test_uploadphoto_out_of_bounds(url):

    _, token, _, _ = create_backend(url)

    url_upload_photo = url + 'user/profile/uploadphoto'

   # Dimensions are 768 x 431
    img_data1 = {
        'token': token,
        'img_url': 'https://img1.looper.com/img/gallery/kermit-the-frogs-history-explained/intro-1601411424.jpg',
        'x_start': -1,
        'y_start': -1,
        'x_end': 40,
        'y_end': 40          
    }

    img_data2 = {
        'token': token,
        'img_url': 'https://img1.looper.com/img/gallery/kermit-the-frogs-history-explained/intro-1601411424.jpg',
        'x_start': 0,
        'y_start': 0,
        'x_end': 983,
        'y_end': 755          
    }

    img_data3 = {
        'token': token,
        'img_url': 'https://img1.looper.com/img/gallery/kermit-the-frogs-history-explained/intro-1601411424.jpg',
        'x_start': -20,
        'y_start': -20,
        'x_end': 40,
        'y_end': 40          
    }

    img_data4 = {
        'token': token,
        'img_url': 'https://img1.looper.com/img/gallery/kermit-the-frogs-history-explained/intro-1601411424.jpg',
        'x_start': 67,
        'y_start': 6232,
        'x_end': 5000,
        'y_end': 300          
    }

    img_data5 = {
        'token': token,
        'img_url': 'https://img1.looper.com/img/gallery/kermit-the-frogs-history-explained/intro-1601411424.jpg',
        'x_start': -20,
        'y_start': -20,
        'x_end': 1000,
        'y_end': 4000          
    }

    assert requests.post(url_upload_photo, json=img_data1).status_code == 400
    assert requests.post(url_upload_photo, json=img_data2).status_code == 400
    assert requests.post(url_upload_photo, json=img_data3).status_code == 400
    assert requests.post(url_upload_photo, json=img_data4).status_code == 400
    assert requests.post(url_upload_photo, json=img_data5).status_code == 400

def test_uploadphoto_success(url):
    _, token, _, _ = create_backend(url)

    url_upload_photo = url + 'user/profile/uploadphoto'

   # Dimensions are 768 x 431
    img_data = {
        'token': token,
        'img_url': 'https://img1.looper.com/img/gallery/kermit-the-frogs-history-explained/intro-1601411424.jpg',
        'x_start': 0,
        'y_start': 0,
        'x_end': 50,
        'y_end': 50
    }

    assert requests.post(url_upload_photo, json=img_data).status_code == 200

def test_uploadphoto_max_dimensions(url):
    _, token, _, _ = create_backend(url)

    url_upload_photo = url + 'user/profile/uploadphoto'

    # Dimensions are 768 x 431
    img_data = {
        'token': token,
        'img_url': 'https://img1.looper.com/img/gallery/kermit-the-frogs-history-explained/intro-1601411424.jpg',
        'x_start': 0,
        'y_start': 0,
        'x_end': 768,
        'y_end': 431
    }
    assert requests.post(url_upload_photo, json=img_data).status_code == 200

def test_uploadphoto_two_users(url):
    _, token1, _, token2 = create_backend(url)

    url_upload_photo = url + 'user/profile/uploadphoto'

    img_data1 = {
        'token': token1,
        'img_url': 'https://img1.looper.com/img/gallery/kermit-the-frogs-history-explained/intro-1601411424.jpg',
        'x_start': 0,
        'y_start': 0,
        'x_end': 450,
        'y_end': 400
    }
    # Image is 786 x 326
    img_data2 = {
        'token': token2,
        'img_url': 'https://www.humanesociety.org/sites/default/files/styles/768x326/public/2020-07/dog-366503.jpg?h=e22bf01e&itok=W45qqZzt',
        'x_start': 0,
        'y_start': 0,
        'x_end': 500,
        'y_end': 250
    }

    assert requests.post(url_upload_photo, json=img_data1).status_code == 200
    assert requests.post(url_upload_photo, json=img_data2).status_code == 200


