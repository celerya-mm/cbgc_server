from datetime import datetime

from flask import request, jsonify, current_app as app

from app.models.certificates_cons import CertificateCons
from app.models.tokens import AuthToken


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
            farmers_list = CertificateCons.query.all()
            return jsonify([farmer.to_dict() for farmer in farmers_list]), 200


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
                return jsonify(
                    id=certificate_cons.id,
                    certificate_nr=certificate_cons.certificate_nr,
                    certificate_date=datetime.strftime(certificate_cons.certificate_date, "%Y-%m-%d"),
                    certificate_year=certificate_cons.certificate_year,
                    cockade_id=certificate_cons.cockade_id,
                    sale_type=certificate_cons.sale_type,
                    sale_quantity=certificate_cons.sale_quantity,
                    note=certificate_cons.note,
                    head_id=certificate_cons.head_id,
                    farmer_id=certificate_cons.farmer_id,
                    buyer_id=certificate_cons.buyer_id,
                    slaughterhouse_id=certificate_cons.slaughterhouse_id,
                    certificate_pdf=certificate_cons.certificate_pdf,
                    created_at=datetime.strftime(certificate_cons.created_at, "%Y-%m-%d %H:%M:%S"),
                    updated_at=datetime.strftime(certificate_cons.updated_at, "%Y-%m-%d %H:%M:%S")
                ), 200
            else:
                return jsonify(error=f'Certificato CONSORZIO not found with id: {certificate_cons_id}'), 404
