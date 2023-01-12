from datetime import datetime

from flask import request, jsonify, current_app as app

from app.models.slaughterhouses import Slaughterhouse
from app.models.tokens import AuthToken


@app.route('/api/slaughterhouses/', methods=['GET'])
def get_slaughterhouses():
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
            farmers_list = Slaughterhouse.query.all()
            return jsonify([farmer.to_dict() for farmer in farmers_list]), 200


@app.route('/api/slaughterhouse/<int:slaughterhouse_id>', methods=['GET'])
def get_slaughterhouse(slaughterhouse_id):
    """API ricezione elenco allevatori."""
    token = request.headers.get("token")
    if not token:
        return jsonify({"message": "Please log in."}), 401
    else:
        authenticated = AuthToken.query.filter(AuthToken.token == token).first()
        if authenticated in ["", None] or authenticated.expires_at < datetime.now():
            return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
        else:
            slaughterhouse = Slaughterhouse.query.filter_by(id=slaughterhouse_id).first()
            if slaughterhouse:
                if slaughterhouse.affiliation_start_date:
                    affiliation_start_date = datetime.strftime(slaughterhouse.affiliation_start_date, "%Y-%m-%d")
                else:
                    affiliation_start_date = slaughterhouse.affiliation_start_date

                if slaughterhouse.affiliation_end_date:
                    affiliation_end_date = datetime.strftime(slaughterhouse.affiliation_end_date, "%Y-%m-%d")
                else:
                    affiliation_end_date = slaughterhouse.affiliation_end_date

                return jsonify(
                    id=slaughterhouse.id,
                    slaughterhouse=slaughterhouse.slaughterhouse,
                    email=slaughterhouse.email,
                    phone=slaughterhouse.phone,
                    affiliation_start_date=affiliation_start_date,
                    affiliation_end_date=affiliation_end_date,
                    affiliation_status=slaughterhouse.affiliation_status,
                    address=slaughterhouse.address,
                    cap=slaughterhouse.cap,
                    city=slaughterhouse.city,
                    note=slaughterhouse.note,
                    created_at=datetime.strftime(slaughterhouse.created_at, "%Y-%m-%d %H:%M:%S"),
                    updated_at=datetime.strftime(slaughterhouse.updated_at, "%Y-%m-%d %H:%M:%S")
                ), 200
            else:
                return jsonify(error=f'Slaughterhouse not found with id: {slaughterhouse_id}'), 404
