import sys
from json import dumps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from error import InputError

from other import *
from auth import auth_login, auth_logout, auth_register, auth_password_reset, auth_password_reset_request
from user import *
from channel import *
from channels import *
from message import *
from standup import *
from hangman import hangman_guess, hangman_start

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

@APP.route('/user_account_imgs/<path:path>', methods=['GET'])
def return_img(path):
    base_dir = os.path.dirname(os.path.realpath(__file__))
    try:
        return send_from_directory(os.path.join(base_dir, 'user_account_imgs'), path)
    except Exception as e:
        return e

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

# Auth routes
@APP.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    res = auth_register(data['email'], data['password'], data['name_first'], data['name_last'])
    return jsonify(res)

@APP.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    res = auth_login(data['email'], data['password'])
    return jsonify(res)

@APP.route('/auth/logout', methods=['POST'])
def logout():
    data = request.get_json(silent=True)
    res = auth_logout(data['token'])
    return jsonify(res)

@APP.route('/auth/passwordreset/request', methods=['POST'])
def password_reset_request():
    data = request.get_json(silent=True)
    res = auth_password_reset_request(data['email'])
    return jsonify(res)

@APP.route('/auth/passwordreset/reset', methods=['POST'])
def password_reset():
    data = request.get_json(silent=True)
    res = auth_password_reset(data['reset_code'], data['new_password'])
    return jsonify(res)

# Channel routes
@APP.route("/channel/invite", methods=['POST'])
def invite_route():
    data = request.get_json()
    res = invite(data['token'], data['channel_id'], data['u_id'])
    return jsonify(res)

@APP.route("/channel/details", methods=['GET'])
def details_route():
    args = request.args
    res = details(args['token'], args['channel_id'])
    return jsonify(res)

@APP.route("/channel/messages", methods=['GET'])
def messages_route():
    args = request.args
    res = messages(args['token'], args['channel_id'], args['start'])
    return jsonify(res)

@APP.route("/channel/leave", methods=['POST'])
def leave_route():
    data = request.get_json()
    res = leave(data['token'], data['channel_id'])
    return jsonify(res)

@APP.route("/channel/join", methods=['POST'])
def join_route():
    data = request.get_json()
    res = join(data['token'], data['channel_id'])
    return jsonify(res)

@APP.route("/channel/addowner", methods=['POST'])
def addowner_route():
    data = request.json
    res = addowner(data['token'], data['channel_id'], data['u_id'])
    return jsonify(res)

@APP.route("/channel/removeowner", methods=['POST'])
def removeowner_route():
    data = request.json
    res = removeowner(data['token'], data['channel_id'], data['u_id'])
    return jsonify(res)

# Channels routes
@APP.route('/channels/list', methods=['GET'])
def list_route():
    args = request.args
    return jsonify(channels_list(args['token']))

@APP.route('/channels/listall', methods=['GET'])
def listall_route():
    args = request.args
    return jsonify(channels_listall(args['token']))

@APP.route('/channels/create', methods=['POST'])
def create():
    data = request.json
    return jsonify(channels_create(data['token'], data['name'], data['is_public']))

# Message routes
@APP.route("/message/send", methods=['POST'])
def send_flask():
    '''sending a message to a channel'''
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    if channel_id != '':
        channel_id = int(channel_id)
    message = data['message']
    return jsonify(message_send(token, channel_id, message))

@APP.route("/message/remove", methods=['DELETE'])
def remove_flask():
    '''removing a message from a channel'''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    if message_id != '':
        message_id = int(message_id)
    return jsonify(message_remove(token, message_id))

@APP.route("/message/edit", methods=['PUT'])
def edit_flask():
    '''editing a message in a channel'''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    if message_id != '':
        message_id = int(message_id)
    message = data['message']
    return jsonify(message_edit(token, message_id, message))

@APP.route("/message/sendlater", methods=['POST'])
def sendlater_flask():
    '''sending a message at a later time'''
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    if channel_id != '':
        channel_id = int(channel_id)
    message = data['message']
    time_sent = int(data['time_sent'])
    return jsonify(message_sendlater(token, channel_id, message, time_sent))

@APP.route("/message/react", methods=['POST'])
def react_flask():
    '''reacts to a message'''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    if message_id != '':
        message_id = int(message_id)
    react_id = data['react_id']
    if react_id != '':
        react_id = int(react_id)
    return jsonify(message_react(token, message_id, react_id))

@APP.route("/message/unreact", methods=['POST'])
def unreact_flask():
    '''unreacts to a message'''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    if message_id != '':
        message_id = int(message_id)
    react_id = data['react_id']
    if react_id != '':
        react_id = int(react_id)
    return jsonify(message_unreact(token, message_id, react_id))


@APP.route("/message/pin", methods=['POST'])
def pin_flask():
    '''pinning a message'''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    if message_id != '':
        message_id = int(message_id)
    return jsonify(message_pin(token, message_id))

@APP.route("/message/unpin", methods=['POST'])
def unpin_flask():
    '''unpinning a message'''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    if message_id != '':
        message_id = int(message_id)
    return jsonify(message_unpin(token, message_id))

# User routes
@APP.route('/user/profile', methods=['GET'])
def profile():
    args = request.args
    u_id = int(args['u_id']) if args['u_id'] != '' else args['u_id']
    return jsonify(user_profile(args['token'], u_id))

@APP.route('/user/profile/setname', methods=['PUT'])
def setname():
    data = request.get_json(silent=True)
    return jsonify(user_profile_setname(data['token'], data['name_first'], data['name_last']))

@APP.route('/user/profile/setemail', methods=['PUT'])
def setemail():
    data = request.get_json(silent=True)
    return jsonify(user_profile_setemail(data['token'], data['email']))

@APP.route('/user/profile/sethandle', methods=['PUT'])
def sethandle():
    data = request.get_json(silent=True)
    return jsonify(user_profile_sethandle(data['token'], data['handle_str']))

@APP.route('/user/profile/uploadphoto', methods=['POST'])
def uploadphoto():
    data = request.json
    return jsonify(user_upload_photo(data['token'], data['img_url'], data['x_start'], data['y_start'], data['x_end'], data['y_end']))

# Other routes
@APP.route("/clear", methods=['DELETE'])
def clear_route():
    return jsonify(clear())

@APP.route('/users/all', methods=['GET'])
def usersall_route():
    args = request.args
    return jsonify(users_all(args['token']))

@APP.route("/admin/userpermission/change", methods=['POST'])
def admin_userpermission_change_route():
    data = request.json
    u_id = int(data['u_id']) if data['u_id'] else data['u_id']
    p_id = int(data['permission_id']) if data['permission_id'] else data['permission_id']
    return jsonify(admin_userpermission_change(data['token'], u_id, p_id))

@APP.route("/search", methods=['GET'])
def search_route():
    data = request.args
    return jsonify(search(data['token'], data['query_str']))

@APP.route("/standup/start", methods=['POST'])
def standup_start_route():
    data = request.json
    channel_id = int(data['channel_id']) if data['channel_id'] else data['channel_id']
    length = int(data['length']) if data['length'] else data['length']
    return jsonify(standup_start(data['token'], channel_id, length))

@APP.route("/standup/active", methods=['GET'])
def standup_active_route():
    data = request.args
    channel_id = int(data['channel_id']) if data['channel_id'] else data['channel_id']
    return jsonify(standup_active(data['token'], channel_id))

@APP.route("/standup/send", methods=['POST'])
def standup_route_route():
    data = request.json
    channel_id = int(data['channel_id']) if data['channel_id'] else data['channel_id']
    return jsonify(standup_send(data['token'], channel_id, data['message']))

@APP.route("/hangman/start", methods=['POST'])
def hangman_start_route():
    data = request.json
    return jsonify(hangman_start(data['token'], data['channel_id']))

@APP.route("/hangman/guess", methods=['POST'])
def hangman_guess_route():
    data = request.json
    return jsonify(hangman_guess(data['letter'], data['channel_id']))

if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
