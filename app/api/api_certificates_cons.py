from datetime import datetime

from flask import request, jsonify, current_app as app

from app.models.certificates_cons import CertificateCons
from app.models.auth_tokens import AuthToken


@app.route('/api/certificates_cons/', methods=['GET'])
def get_certificates_cons():
	"""API ricezione elenco allevatori."""
	token = request.headers.get("token")
	if not token:
		return jsonify({"message": "Please log in."}), 401
	else:
		authenticated = AuthToken.query.filter(AuthToken.token == token).first()
		if authenticated in ["", None] or authenticated.expires_at < datetime.now():
			return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
		else:
			certificates_list = CertificateCons.query.all()
			return jsonify([cert.to_dict() for cert in certificates_list]), 200


@app.route('/api/certificate_cons/<int:certificate_cons_id>', methods=['GET'])
def get_certificate_cons(certificate_cons_id):
	"""API ricezione elenco allevatori."""
	token = request.headers.get("token")
	if not token:
		return jsonify({"message": "Please log in."}), 401
	else:
		authenticated = AuthToken.query.filter(AuthToken.token == token).first()
		if authenticated in ["", None] or authenticated.expires_at < datetime.now():
			return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
		else:
			certificate_cons = CertificateCons.query.filter_by(id=certificate_cons_id).first()
			if certificate_cons:
				return jsonify(certificate_cons.to_dict()), 200
			else:
				return jsonify(error=f'Certificato CONSORZIO not found with id: {certificate_cons_id}'), 404
