from datetime import datetime

from flask import request, jsonify, current_app as app

from app.models.farmers import Farmer
from app.models.tokens import AuthToken


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
                if farmer.affiliation_start_date:
                    affiliation_start_date = datetime.strftime(farmer.affiliation_start_date, "%Y-%m-%d")
                else:
                    affiliation_start_date = farmer.affiliation_start_date

                if farmer.affiliation_end_date:
                    affiliation_end_date = datetime.strftime(farmer.affiliation_end_date, "%Y-%m-%d")
                else:
                    affiliation_end_date = farmer.affiliation_end_date

                return jsonify(
                    id=farmer.id,
                    farmer_name=farmer.farmer_name,
                    email=farmer.email,
                    phone=farmer.phone,
                    user_id=farmer.user_id,
                    affiliation_start_date=affiliation_start_date,
                    affiliation_end_date=affiliation_end_date,
                    affiliation_status=farmer.affiliation_status,
                    address=farmer.address,
                    cap=farmer.cap,
                    city=farmer.city,
                    note=farmer.note,
                    created_at=datetime.strftime(farmer.created_at, "%Y-%m-%d %H:%M:%S"),
                    updated_at=datetime.strftime(farmer.updated_at, "%Y-%m-%d %H:%M:%S")
                ), 200
            else:
                return jsonify(error=f'Farmer not found with id: {farmer_id}'), 404
