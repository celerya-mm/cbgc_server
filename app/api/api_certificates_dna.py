from datetime import datetime
import json

from flask import request, jsonify, make_response
from flask import current_app as app

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
            farmers_list = CertificateDna.query.all()
            return jsonify([farmer.to_dict() for farmer in farmers_list]), 200


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
                return jsonify(
                    id=certificate_dna.id,
                    dna_cert_id=certificate_dna.dna_cert_id,
                    dna_cert_nr=certificate_dna.dna_cert_nr,
                    dna_cert_date=datetime.strftime(certificate_dna.dna_cert_date, "%Y-%m-%d"),
                    dna_cert_year=certificate_dna.dna_cert_year,
                    note=certificate_dna.note,
                    head_id=certificate_dna.head_id,
                    farmer_id=certificate_dna.farmer_id,
                    created_at=datetime.strftime(certificate_dna.created_at, "%Y-%m-%d %H:%M:%S"),
                    updated_at=datetime.strftime(certificate_dna.updated_at, "%Y-%m-%d %H:%M:%S")
                ), 200
            else:
                return jsonify(error=f'Certificate_DNA not found with id: {certificate_dna_id}'), 404
