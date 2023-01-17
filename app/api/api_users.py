import hashlib
from datetime import datetime

from flask import request, jsonify, make_response, current_app as app

from app.app import db
from app.models.accounts import User
from app.models.tokens import AuthToken
from app.utilitys.functions_accounts import (is_valid_email, __save_auth_token, __generate_auth_token, psw_hash,
                                             psw_verify, psw_contain_usr)


@app.route('/api/user_signup/', methods=['POST'])
def user_signup():
    """API creazione utente servizio."""
    data_received = request.get_json()
    username = data_received['username'].replace(" ", "")
    password = data_received['password'].replace(" ", "")
    try:
        verify_password = psw_verify(password)
        if verify_password is not False:
            return make_response(jsonify(verify_password), 400)

        contain_usr = psw_contain_usr(password, username)
        if contain_usr is not False:
            return make_response(jsonify(contain_usr), 400)

        valid_email = is_valid_email(data_received['email'])
        if valid_email:
            if username not in [None, ""] and \
                    password not in [None, ""] and \
                    data_received['email'] not in [None, ""]:

                existing_user = User.query.filter(User.username == data_received['username']).first()
                if existing_user is None:
                    new_user = User(
                        username=username,
                        password=psw_hash(str(data_received['password'])),
                        name=data_received['name'],
                        last_name=data_received["last_name"],
                        phone=data_received['phone'],
                        email=data_received["email"],
                        note=data_received["note"]
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    print('NEW user ID: {}'.format(new_user.id))

                    data = {
                        'status': 'success',
                        'data': {
                            'id': new_user.id,
                            'username': new_user.username,
                            'full_name': new_user.full_name,
                            'phone': new_user.phone,
                            'email': new_user.email,
                            'note': new_user.note
                        }
                    }
                    response = make_response(jsonify(data), 201)
                else:
                    data = {
                        'status': 'failed',
                        'message': 'User {} already exists.'.format(username)
                    }
                    response = make_response(jsonify(data), 401)
            else:
                data = {
                    'status': 'failed',
                    'message': 'Username, Password and email are required.',
                    'data': {
                        'username': username,
                        'email': data_received['email']
                    }
                }
                response = make_response(jsonify(data), 400)
        else:
            data = {
                'status': 'failed',
                'message': 'The email passed is not a valid email.',
                'data': {
                    'email': data_received['email']}

            }
            response = make_response(jsonify(data), 400)
    except Exception as error:
        data = {
            'status': 'failed',
            'message': 'An error occurred: {}.'.format(error)
        }
        response = make_response(jsonify(data), 400)
    return response


@app.route('/api/user_login/', methods=['POST'])
def authenticate_user():
    """API autenticazione utente servizio."""
    data_received = request.get_json()
    username = data_received['username'].replace(" ", "")
    password = data_received['password'].replace(" ", "")

    _user = User.query.filter(
        User.username == username,
        User.password == hashlib.sha256(str(password).encode('utf-8')).hexdigest()
    ).first()

    try:
        if _user not in [None, ""]:
            record = len(_user.auth_tokens) - 1
            if record > 0 and _user.auth_tokens[record].expires_at > datetime.now():
                token = _user.auth_tokens[record].token
                data = {
                    'status': 'success',
                    'data': {
                        'token': token,
                        'expiration': datetime.strftime(_user.auth_tokens[record].expires_at, "%Y-%m-%d %H:%M:%S"),
                        'user_id': _user.id
                    }
                }
                response = make_response(jsonify(data), 201)
            else:
                token = __generate_auth_token()
                save = __save_auth_token("", _user.id, token)
                data = {
                    'status': 'success',
                    'data': {
                        'token': token,
                        'expiration': datetime.strftime(save.expires_at, "%Y-%m-%d %H:%M:%S"),
                        'user_id': _user.id
                    }
                }
                response = make_response(jsonify(data), 201)
        else:
            data = {
                'status': 'failed',
                'message': f"Login failed, there's no user registered with this username e password.",
                'data': {
                    "user": username
                }
            }
            response = make_response(jsonify(data), 500)
    except Exception as error:
        data = {
            'status': 'failed',
            'message': 'An error occurred: {}.'.format(error)
        }
        response = make_response(jsonify(data), 400)
    return response


@app.route('/api/users/', methods=['GET'])
def get_users_list():
    """API ricezione elenco allevatori."""
    token = request.headers.get("token")
    if not token:
        return jsonify({"message": "Please log in."}), 401
    else:
        authenticated = AuthToken.query.filter(AuthToken.token == token).first()
        if authenticated in ["", None] or authenticated.expires_at < datetime.now():
            return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
        else:
            users_list = User.query.all()
            return jsonify([user.to_dict() for user in users_list]), 200


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """API ricezione elenco allevatori."""
    token = request.headers.get("token")
    print("TOKEN", token)
    if not token:
        return jsonify({"message": "Please log in."}), 401
    else:
        authenticated = AuthToken.query.filter(AuthToken.token == token).first()
        if authenticated in ["", None] or authenticated.expires_at < datetime.now():
            return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
        else:
            user = User.query.filter_by(id=user_id).first()
            if user:
                return jsonify(user.to_dict()), 200
            else:
                return jsonify(error=f'User not found with id: {user_id}'), 404
