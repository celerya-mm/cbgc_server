import hashlib
from datetime import datetime

from flask import request, jsonify, make_response, current_app as app

from app.app import db
from app.models.accounts import Administrator
from app.models.tokens import AuthToken
from app.utility import psw_function as pswf
from app.utility.functions_accounts import is_valid_email, __save_auth_token, __generate_auth_token


@app.route('/api/admin_signup/', methods=['POST'])
def administrator_signup():
    """API creazione utente amministratore."""
    data_received = request.get_json()
    username = data_received['username']
    password = data_received['password']
    name = data_received['name']
    last_name = data_received['last_name']
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
                existing_user = Administrator.query.filter(Administrator.username == username).first()
                if existing_user is None:
                    new_admin = Administrator(
                        username=username,
                        password=hashlib.sha256(str(password).encode('utf-8')).hexdigest(),
                        name=name,
                        last_name=last_name,
                        email=email,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.session.add(new_admin)
                    db.session.commit()
                    print('NEW admin ID: {}'.format(new_admin.id))
                    token = __generate_auth_token()
                    save = __save_auth_token(new_admin.id, "", token)
                    print('Generated auth token successfully.')
                    data = {
                        '01_status': 'success',
                        'token': token,
                        'expiration': save.expires_at,
                        'id': new_admin.id,
                        'username': new_admin.username,
                        'email': new_admin.email
                    }
                    response = make_response(jsonify(data), 201)
                else:
                    data = {
                        '01_status': 'failed',
                        '02_message': 'Administrator {} already exists.'.format(username)
                    }
                    response = make_response(jsonify(data), 401)
            except Exception as error:
                data = {
                    '01_status': 'failed',
                    '02_message': 'Administrator registration failed: {}.'.format(error)
                }
                response = make_response(jsonify(data), 500)
        else:
            data = {
                '01_status': 'failed',
                '02_message': 'Username, Password and email are required.',
                'username': username,
                'password': '*******',
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


@app.route('/api/admin_login/', methods=['POST'])
def authenticate_administrator():
    """API login utente amministratore."""
    data_received = request.get_json()
    username = data_received["username"]
    password = data_received["password"]

    authenticated = Administrator.query.filter(
        Administrator.username == username,
        Administrator.password == hashlib.sha256(str(password).encode('utf-8')).hexdigest()
    ).first()
    try:
        if authenticated not in [None, ""]:
            record = len(authenticated.auth_token) - 1
            if authenticated.auth_token[record].expires_at > datetime.now():
                token = authenticated.auth_token[record].token
                data = {
                    '01_status': 'success',
                    'token': token,
                    'expiration': authenticated.auth_token[record].expires_at,
                    'id': authenticated.id,
                    'username': authenticated.username,
                    'email': authenticated.email
                }
                response = make_response(jsonify(data), 201)
            else:
                token = __generate_auth_token()
                save = __save_auth_token(authenticated.id, "", token)
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
                '02_message': f"Login failed, there's no administrator registered with this username e password.",
                'username': username
            }
            response = make_response(jsonify(data), 500)
    except Exception as error:
        data = {
            '01_status': 'failed',
            '02_message': 'An error occurred: {}.'.format(error)
        }
        response = make_response(jsonify(data), 400)
    return response


@app.route('/api/admins/', methods=['GET'])
def get_admins_list():
    """API ricezione elenco allevatori."""
    token = request.headers.get("token")
    if not token:
        return jsonify({"message": "Please log in."}), 401
    else:
        authenticated = AuthToken.query.filter(AuthToken.token == token).first()
        if authenticated in ["", None] or authenticated.expires_at < datetime.now():
            return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
        else:
            admins_list = Administrator.query.all()
            return jsonify([admin.to_dict() for admin in admins_list]), 200


@app.route('/api/admin/<int:admin_id>', methods=['GET'])
def get_admin(admin_id):
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
            admin = Administrator.query.filter_by(id=admin_id).first()
            if admin:
                return jsonify(
                    id=admin.id,
                    username=admin.username,
                    name=admin.name,
                    last_name=admin.last_name,
                    email=admin.email,
                    created_at=datetime.strftime(admin.created_at, "%Y-%m-%d %H:%M:%S"),
                    updated_at=datetime.strftime(admin.updated_at, "%Y-%m-%d %H:%M:%S")
                ), 200
            else:
                return jsonify(error=f'User Administrator not found with id: {admin_id}'), 404
