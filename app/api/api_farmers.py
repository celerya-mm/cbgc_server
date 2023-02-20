from datetime import datetime

from flask import request, jsonify, current_app as app

from app.models.farmers import Farmer
from app.models.auth_tokens import AuthToken


@app.route('/api/farmers/', methods=['GET'])
def get_farmers():
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
			farmers_list = Farmer.query.all()
			return jsonify([farmer.to_dict() for farmer in farmers_list]), 200


@app.route('/api/farmer/<int:farmer_id>', methods=['GET'])
def get_farmer(farmer_id):
	"""API ricezione elenco allevatori."""
	token = request.headers.get("token")
	if not token:
		return jsonify({"message": "Please log in."}), 401
	else:
		authenticated = AuthToken.query.filter(AuthToken.token == token).first()
		if authenticated in ["", None] or authenticated.expires_at < datetime.now():
			return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
		else:
			farmer = Farmer.query.filter_by(id=farmer_id).first()
			if farmer:
				return jsonify(farmer.to_dict()), 200
			else:
				return jsonify(error=f'Farmer not found with id: {farmer_id}'), 404
