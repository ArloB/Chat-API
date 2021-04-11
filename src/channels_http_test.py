'''
Channels HTTP Test
'''
import requests
import other

register_data1 = {
    'email': 'email@email.com',
    'password': 'password',
    'name_first': 'first',
    'name_last': 'last'
}

register_data2 = {
    'email': 'other@email.com',
    'password': 'computer',
    'name_first': 'Jim',
    'name_last': 'Halpert'
}

# Channels_list tests

def test_channels_list_one(url):
    '''
    Registers a user, creates new channel and tests channels_list
    '''

    url_register = url + 'auth/register'
    url_ch_create = url + 'channels/create'
    url_ch_list = url + 'channels/list'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict = resp.json()
    _ = user_dict['u_id']
    token = user_dict['token']

    channel_data = {
        'name': 'Tree',
        'is_public': False,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data)
    ch_dict = resp.json()
    ch_id = ch_dict['channel_id']
    resp = requests.get(url_ch_list, params=user_dict)
    channel_list = resp.json()
    assert channel_list['channels'] == [{'name': 'Tree', \
        'channel_id': ch_id}]
    

def test_channels_list_empty(url):
    '''
    Registers new user, tests channels_list, should return empty dictionary
    '''

    url_register = url + 'auth/register'
    url_ch_list = url + 'channels/list'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict = resp.json()
    resp = requests.get(url_ch_list, params=user_dict)
    channel_list = resp.json()
    assert channel_list['channels'] == []

def test_channels_list_otheruser(url):

    url_register = url + 'auth/register'
    url_logout = url + 'auth/logout'
    url_ch_create = url + 'channels/create'
    url_ch_list = url + 'channels/list'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict1 = resp.json()
    token = user_dict1['token']

    channel_data1 = {
        'name': 'Tree',
        'is_public': False,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data1)
    _ = resp.json()
    resp = requests.post(url_logout, json=user_dict1)
    resp = requests.post(url_register, json=register_data2)
    user_dict2 = resp.json()
    _ = user_dict2['u_id']
    token = user_dict2['token']

    channel_data2 = {
        'name': 'Apple',
        'is_public': False,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data2)
    ch_dict2 = resp.json()
    ch_id = ch_dict2['channel_id']
    resp = requests.get(url_ch_list, params=user_dict2)
    channel_list = resp.json()
    assert channel_list['channels'] == [{'name': 'Apple', 'channel_id': \
        ch_id}]

# Channels_listall tests

def test_channels_listall_one(url):

    url_register = url + 'auth/register'
    url_ch_create = url + 'channels/create'
    url_ch_listall = url + 'channels/listall'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict = resp.json()
    _ = user_dict['u_id']
    token = user_dict['token']

    channel_data = {
        'name': 'Tree',
        'is_public': False,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data)
    ch_dict = resp.json()
    ch_id = ch_dict['channel_id']
    resp = requests.get(url_ch_listall, params=user_dict)
    channel_list = resp.json()
    assert channel_list['channels'] == [{'name': 'Tree', 'channel_id': \
        ch_id}]

def test_channels_listall_two(url):

    url_register = url + 'auth/register'
    url_ch_create = url + 'channels/create'
    url_ch_listall = url + 'channels/listall'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict = resp.json()
    _ = user_dict['u_id']
    token = user_dict['token']

    channel_data1 = {
        'name': 'Tree',
        'is_public': False,
        'token': token
    }
    channel_data2 = {
        'name': 'Apple',
        'is_public': False,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data1)
    ch_dict1 = resp.json()
    ch_id1 = ch_dict1['channel_id']
    resp = requests.post(url_ch_create, json=channel_data2)
    ch_dict2 = resp.json()
    ch_id2 = ch_dict2['channel_id']
    resp = requests.get(url_ch_listall, params=user_dict)
    channel_list = resp.json()
    assert channel_list['channels'] == [{'channel_id': ch_id1, 'name': \
        'Tree'},{'channel_id': ch_id2, 'name': 'Apple'}]

def test_channels_listall_otheruser(url):

    url_register = url + 'auth/register'
    url_logout = url + 'auth/logout'
    url_ch_create = url + 'channels/create'
    url_ch_listall = url + 'channels/listall'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict1 = resp.json()
    _ = user_dict1['u_id']
    token = user_dict1['token']

    channel_data1 = {
        'name': 'Tree',
        'is_public': False,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data1)
    ch_dict1 = resp.json()
    ch_id1 = ch_dict1['channel_id']
    resp = requests.post(url_logout, json=user_dict1)
    resp = requests.post(url_register, json=register_data2)
    user_dict2 = resp.json()
    _ = user_dict2['u_id']
    token = user_dict2['token']

    channel_data2 = {
        'name': 'Apple',
        'is_public': False,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data2)
    ch_dict2 = resp.json()
    ch_id2 = ch_dict2['channel_id']
    resp = requests.get(url_ch_listall, params=user_dict2)
    channel_list = resp.json()
    assert channel_list['channels'] == [{'channel_id': \
        ch_id1, 'name': 'Tree'}, {'channel_id': ch_id2, \
        'name': 'Apple'}]

# Channels_create tests

def test_channels_create_success(url):

    url_register = url + 'auth/register'
    url_ch_create = url + 'channels/create'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict = resp.json()
    token = user_dict['token']

    channel_data = {
        'name': 'Test',
        'is_public': False,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data)
    ch_dict = resp.json()
    ch_id = ch_dict['channel_id']
    assert resp.status_code == 200
    assert ch_dict == {'channel_id': ch_id}

def test_channels_create_two(url):

    url_register = url + 'auth/register'
    url_ch_create = url + 'channels/create'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict = resp.json()
    token = user_dict['token']

    channel_data1 = {
        'name': 'Mango',
        'is_public': True,
        'token': token
    }
    channel_data2 = {
        'name': 'Banana',
        'is_public': False,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data1)
    assert resp.ok
    ch_dict1 = resp.json()
    ch_id1 = ch_dict1['channel_id']
    resp = requests.post(url_ch_create, json=channel_data2)
    ch_dict2 = resp.json()
    ch_id2 = ch_dict2['channel_id']
    assert resp.status_code == 200
    assert ch_dict1 == {'channel_id': ch_id1}
    assert ch_dict2 == {'channel_id': ch_id2}

def test_channels_create_too_long_one(url):

    url_register = url + 'auth/register'
    url_ch_create = url + 'channels/create'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict = resp.json()
    token = user_dict['token']

    channel_data1 = {
        'name': 'Thisnameiswaytoolong1234',
        'is_public': True,
        'token': token
    }
    channel_data2 = {
        'name': 'randomlygeneratedpassword369',
        'is_public': False,
        'token': token
    }

    assert requests.post(url_ch_create, json=channel_data1).status_code == 400
    assert requests.post(url_ch_create, json=channel_data2).status_code == 400

def test_channels_create_too_long_two(url):

    url_register = url + 'auth/register'
    url_ch_create = url + 'channels/create'

    other.clear()
    resp = requests.post(url_register, json=register_data1)
    user_dict = resp.json()
    token = user_dict['token']

    channel_data1 = {
        'name': 'Apple',
        'is_public': True,
        'token': token
    }
    channel_data2 = {
        'name': 'Pear',
        'is_public': False,
        'token': token
    }
    channel_data3 = {
        'name': 'Hellohellohellohellohellohellohellohello',
        'is_public': True,
        'token': token
    }

    resp = requests.post(url_ch_create, json=channel_data1)
    resp = requests.post(url_ch_create, json=channel_data2)
    assert requests.post(url_ch_create, json=channel_data3).status_code == 400
