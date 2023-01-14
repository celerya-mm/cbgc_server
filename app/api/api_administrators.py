from datetime import datetime

from flask import request, jsonify, make_response, current_app as app

from app.app import db
from app.models.accounts import Administrator
from app.models.tokens import AuthToken
from app.utility.psw_function import psw_contain_usr, psw_verify, psw_hash
from app.utility.functions_accounts import is_valid_email, __save_auth_token, __generate_auth_token


@app.route('/api/admin_signup/', methods=['POST'])
def administrator_signup():
    """API creazione utente amministratore."""
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

        valid_email = is_valid_email(data_received["email"])
        if valid_email:
            if username not in [None, ""] and  password not in [None, ""] and \
                    data_received["email"] not in [None, ""]:
                try:
                    existing_user = Administrator.query.filter(Administrator.username == username).first()
                    if existing_user is None:
                        new_admin = Administrator(
                            username=username,
                            password=psw_hash(str(data_received['password'])),
                            name=data_received['name'],
                            last_name=data_received["last_name"],
                            phone=data_received['phone'],
                            email=data_received["email"],
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
                            'phone': new_admin.phone,
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
                    'username': data_received['username'],
                    'email': data_received["email"]
                }
                response = make_response(jsonify(data), 400)
        else:
            data = {
                '01_status': 'failed',
                '02_message': 'The email passed is not a valid email.',
                'email': data_received["email"]
            }
            response = make_response(jsonify(data), 400)
    except Exception as error:
        data = {
            '01_status': 'failed',
            '02_message': 'An error occurred: {}.'.format(error)
        }
        response = make_response(jsonify(data), 400)
    return response


@app.route('/api/admin_login/', methods=['POST'])
def authenticate_administrator():
    """API login utente amministratore."""
    data_received = request.get_json()
    username = data_received['username'].replace(" ", "")
    password = data_received['password'].replace(" ", "")

    _admin = Administrator.query.filter(
        Administrator.username == username,
        Administrator.password == psw_hash(str(password))
    ).first()

    if _admin not in [None, ""]:
        record = len(_admin.auth_token) - 1
        if record > 0 and _admin.auth_token[record].expires_at > datetime.now():
            token = _admin.auth_token[record].token
            data = {
                '01_status': 'success',
                'token': token,
                'expiration': _admin.auth_token[record].expires_at,
                'id': _admin.id,
                'username': _admin.username,
                'phone': _admin.phone,
                'email': _admin.email
            }
            response = make_response(jsonify(data), 201)
        else:
            token = __generate_auth_token()
            save = __save_auth_token(_admin.id, "", token)
            data = {
                '01_status': 'success',
                'token': token,
                'expiration': save.expires_at,
                'id': _admin.id,
                'username': _admin.username,
                'phone': _admin.phone,
                'email': _admin.email
            }
            response = make_response(jsonify(data), 201)
    else:
        data = {
            '01_status': 'failed',
            '02_message': f"Login failed, there's no administrator registered with this username e password.",
            'username': username
        }
        response = make_response(jsonify(data), 500)
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
                return jsonify(admin.to_dict()), 200
            else:
                return jsonify(error=f'User Administrator not found with id: {admin_id}'), 404
