from datetime import datetime
from uuid import uuid4

from flask import request, jsonify, current_app as app, make_response

from app.models.accounts import User
from app.models.tokens import AuthToken
from app.utilitys.functions_accounts import psw_hash, __save_auth_token


@app.route('/api/buyer/login/', methods=['POST'])
def buyer_login():
	"""API login utente acquirente."""
	data_received = request.get_json()
	username = data_received['username'].replace(" ", "")
	password = data_received['password'].replace(" ", "")

	_user = User.query.filter_by(username=username, password=psw_hash(str(password))).first()

	if _user not in [None, ""]:
		record = _user.auth_tokens.first()
		if record and record.expires_at > datetime.now():
			data = {
				'status': 'success',
				'data': {
					'token': str(record.token),
					'expiration': datetime.strftime(record.expires_at, "%Y-%m-%d %H:%M:%S"),
					'id': _user.id,
					'username': _user.username,
					'psw_changed': _user.psw_changed
				}
			}
			response = make_response(jsonify(data), 201)
		else:
			token = str(uuid4())
			save = __save_auth_token(token, user_id=_user.id)
			data = {
				'status': 'success',
				'data': {
					'token': token,
					'expiration': datetime.strftime(save.expires_at, "%Y-%m-%d %H:%M:%S"),
					'id': _user.id,
					'username': _user.username,
					'psw_changed': _user.psw_changed
				}
			}
			response = make_response(jsonify(data), 201)
	else:
		data = {
			'status': 'failed',
			'message': f"Login fallita, non è presente nessun acquirente con username e password inseriti."
			           f"Contatta il Consorzio per farti assegnare un utente.",
			'username': username
		}
		response = make_response(jsonify(data), 500)
	return response


@app.route('/api/buyers/', methods=['GET'])
def get_buyers():
	"""API ricezione elenco acquirenti."""
	token = request.headers.get("token")
	print("TOKEN", token)
	if not token:
		return jsonify({"message": "Please log in."}), 401
	else:
		authenticated = AuthToken.query.filter(AuthToken.token == token).first()
		if authenticated in ["", None] or authenticated.expires_at < datetime.now():
			return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
		else:
			buyer_list = User.query.all()
			return jsonify([buyer.to_dict() for buyer in buyer_list]), 200


@app.route('/api/buyer/<int:buyer_id>', methods=['GET'])
def get_buyer(buyer_id):
	"""API ricerca singolo acquirente."""
	token = request.headers.get("token")
	if not token:
		return jsonify({"message": "Please log in."}), 401
	else:
		authenticated = AuthToken.query.filter(AuthToken.token == token).first()
		if authenticated in ["", None] or authenticated.expires_at < datetime.now():
			return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
		else:
			buyer = User.query.filter_by(id=buyer_id).first()
			if buyer:
				return jsonify(buyer.to_dict()), 200
			else:
				return jsonify(error=f'Buyer not found with id: {buyer_id}'), 404
