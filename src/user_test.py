import pytest

from other import clear
from auth import auth_register
from user import *

def create_backend():
    clear()
    user1 = auth_register('email@email.com', 'password', 'first', 'last')
    u_id1 = user1['u_id']
    token1 = user1['token']
    user2 = auth_register('person@gmail.com', 'verystronk', 'apple', 'tree')
    u_id2 = user2['u_id']
    token2 = user2['token']

    return u_id1, token1, u_id2, token2

def register_default_user():
    '''
    Registers User. Remember to clear after testing is done to avoid unintended errors.
    '''
    return auth_register("validemail@gmail.com", "123abc!@#", "Hayden", "Everest")

def get_user_profile(token, u_id):
    '''
    Gets user profile in one easy function. Returns user dict
    '''
    return user_profile(token, u_id)['user']

def test_user_profile():
    '''
    Retrieving User Profile
    '''
    clear()
    result_body = register_default_user()
    token, u_id = result_body['token'], result_body['u_id']
    assert user_profile(token, u_id) == {'user': {
        'u_id': u_id,
        'email': 'validemail@gmail.com',
        'name_first': "Hayden",
        'name_last': "Everest",
        'handle_str': 'ehayden',
        'profile_img_url': ''
    }}

def test_user_setname():
    '''
    Testing Set Name
    '''
    clear()
    result_body = register_default_user()
    token, u_id = result_body['token'], result_body['u_id']
    user_profile_setname(token, 'Jason', 'Yu')
    profile = get_user_profile(token, u_id)
    assert profile['name_first'] == 'Jason'
    assert profile['name_last'] == 'Yu'

def test_user_setemail():
    '''
    Testing Set Email
    '''
    clear()
    result_body = register_default_user()
    token, u_id = result_body['token'], result_body['u_id']
    user_profile_setemail(token, 'newtestemail@email.com')
    profile = get_user_profile(token, u_id)
    assert profile['email'] == 'newtestemail@email.com'

def test_user_sethandle():
    '''
    Testing Set Handle
    '''
    clear()
    result_body = register_default_user()
    token, u_id = result_body['token'], result_body['u_id']
    user_profile_sethandle(token, 'jasonyuhandle')
    profile = get_user_profile(token, u_id)
    assert profile['handle_str'] == 'jasonyuhandle'

# User_uploadphoto Tests

def test_invalid_HTTP_status():
    _, token, _, _ = create_backend()

    img_url = 'http://google.com/404'

    # Url 404s so this should fail
    with pytest.raises(InputError):
        user_upload_photo(token, img_url, 0, 0, 45, 45)

def test_img_not_jpg():
    _, token, _, _ = create_backend()

    # Dimensions are 320 x 350
    img_url1 = 'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png'
    img_url2 = 'https://www.arlo.com/images/Arlov4/home/product-j-1--a.png'

    # Image is not .jpg, this is expected to fail
    with pytest.raises(InputError):
        user_upload_photo(token, img_url1, 0, 0, 45, 45)
        user_upload_photo(token, img_url2, 0, 0, 24, 24)

def test_out_of_bounds():
    _, token, _, _ = create_backend()

    # Dimensions are 768 x 431
    img_url = 'https://img1.looper.com/img/gallery/kermit-the-frogs-history-explained/intro-1601411424.jpg'

    # These tests have x,y-coords out of boundaries therefore this should fail
    with pytest.raises(InputError):
        user_upload_photo(token, img_url, -1, -1, 40, 40)
        user_upload_photo(token, img_url, 0, 0, 983, 756)
        user_upload_photo(token, img_url, -20, -20, 40, 40)
        user_upload_photo(token, img_url, 67, 4, 5000, 3000)
        user_upload_photo(token, img_url, -20, -20, 1000, 5000)

def test_crop_dimension_invalid():
    _, token, _, _ = create_backend()

    # Dimensions are 768 x 512
    img_url = 'https://daily.jstor.org/wp-content/uploads/2018/06/soccer_europe_1050x700.jpg'

    # x_start and y_start are >= x_end and y_end, expected to fail
    with pytest.raises(InputError):
        user_upload_photo(token, img_url, 0, 0, 0, 0)
        user_upload_photo(token, img_url, 250, 250, 250, 250)
        user_upload_photo(token, img_url, 768, 512, 768, 512)
        user_upload_photo(token, img_url, 100, 0, 50, 45)
        user_upload_photo(token, img_url, 0, 250, 45, 200)
        user_upload_photo(token, img_url, 500, 500, 0, 0)
