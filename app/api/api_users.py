import hashlib
from datetime import datetime

from flask import request, jsonify, make_response
from flask import current_app as app

from app.app import db
from app.models.accounts import User
from app.models.tokens import AuthToken
from app.utility import psw_function as pswf
from app.utility.functions_accounts import is_valid_email, __save_auth_token, __generate_auth_token


@app.route('/api/user/', methods=['POST'])
def user_signup():
    """API creazione utente servizio."""
    data_received = request.get_json()
    username = data_received['username']
    password = data_received['password']
    email = data_received['email']

    verify_password = pswf.psw_verify(password)
    if verify_password is not False:
        return make_response(jsonify(verify_password), 400)

    contain_usr = pswf.psw_contain_usr(password, username)
    if contain_usr is not False:
        return make_response(jsonify(contain_usr), 400)

    valid_email = is_valid_email(email)
    if valid_email:
        if username not in [None, ""] and password not in [None, ""] and email not in [None, ""]:
            try:
                existing_user = User.query.filter(User.username == username).first()
                if existing_user is None:
                    new_user = User(
                        username=username,
                        password=hashlib.sha256(str(password).encode('utf-8')).hexdigest(),
                        email=email,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    print('NEW user ID: {}'.format(new_user.id))
                    token = __generate_auth_token()
                    save = __save_auth_token("", new_user.id, token)
                    print('Generated auth token successfully.')
                    data = {
                        '01_status': 'success',
                        'token': token,
                        'expiration': save.expires_at,
                        'id': new_user.id,
                        'username': new_user.username,
                        'email': new_user.email
                    }
                    response = make_response(jsonify(data), 201)
                else:
                    data = {
                        '01_status': 'failed',
                        '02_message': 'User {} already exists.'.format(username)
                    }
                    response = make_response(jsonify(data), 401)
            except Exception as error:
                data = {
                    '01_status': 'failed',
                    '02_message': 'User registration failed. {}.'.format(error)
                }
                response = make_response(jsonify(data), 500)
        else:
            data = {
                '01_status': 'failed',
                '02_message': 'Username, Password and email are required.',
                'username': username,
                'password': '*****',
                'email': email
            }
            response = make_response(jsonify(data), 400)
    else:
        data = {
            '01_status': 'failed',
            '02_message': 'The email passed is not a valid email.',
            'email': email
        }
        response = make_response(jsonify(data), 400)
    return response


@app.route('/api/user_login/', methods=['POST'])
def authenticate_user():
    """API autenticazione utente servizio."""
    data_received = request.get_json()
    username = data_received['username']
    password = data_received['password']

    authenticated = User.query.filter(
        User.username == username,
        User.password == hashlib.sha256(str(password).encode('utf-8')).hexdigest()
    ).first()
    print(hashlib.sha256(str(password).encode('utf-8')).hexdigest())
    try:
        if authenticated not in [None, ""]:
            token = __generate_auth_token()
            if len(authenticated.auth_token) > 0:
                token = authenticated.auth_token[0].token \
                    if authenticated.auth_token[0].expires_at <= datetime.now()\
                    else authenticated.auth_token[0].token
                data = {
                    '01_status': 'success',
                    'token': token,
                    'expiration': authenticated.auth_token[0].expires_at,
                    'id': authenticated.id,
                    'username': authenticated.username,
                    'email': authenticated.email
                }
                response = make_response(jsonify(data), 201)
            else:
                save = __save_auth_token("", authenticated.id, token)
                data = {
                    '01_status': 'success',
                    'token': token,
                    'expiration': save.expires_at,
                    'id': authenticated.id,
                    'username': authenticated.username,
                    'email': authenticated.email
                }
                response = make_response(jsonify(data), 201)
        else:
            data = {
                '01_status': 'failed',
                '02_message': f"Login failed, there's no user registered with this username e password.",
                "user": username,
                "password": '*****'
            }
            response = make_response(jsonify(data), 500)
    except Exception as error:
        data = {
            '01_status': 'failed',
            '02_message': 'An error occurred: {}.'.format(error)
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
            admins_list = User.query.all()
            return jsonify([admin.to_dict() for admin in admins_list]), 200


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
                return jsonify(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    created_at=datetime.strftime(user.created_at, "%Y-%m-%d %H:%M:%S"),
                    updated_at=datetime.strftime(user.updated_at, "%Y-%m-%d %H:%M:%S")
                ), 200
            else:
                return jsonify(error=f'User not found with id: {user_id}'), 404