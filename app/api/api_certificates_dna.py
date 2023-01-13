from datetime import datetime

from flask import request, jsonify, current_app as app

from app.models.certificates_dna import CertificateDna
from app.models.tokens import AuthToken


@app.route('/api/certificates_dna/', methods=['GET'])
def get_certificates_dna():
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
            certificates_list = CertificateDna.query.all()
            return jsonify([cert.to_dict() for cert in certificates_list]), 200


@app.route('/api/certificate_dna/<int:certificate_dna_id>', methods=['GET'])
def get_certificate_dna(certificate_dna_id):
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
            certificate_dna = CertificateDna.query.filter_by(id=certificate_dna_id).first()
            if certificate_dna:
                return jsonify(certificate_dna.to_dict()), 200
            else:
                return jsonify(error=f'Certificate_DNA not found with id: {certificate_dna_id}'), 404
