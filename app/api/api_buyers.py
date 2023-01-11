from datetime import datetime

from flask import request, jsonify, make_response
from flask import current_app as app

from app.models.buyers import Buyer
from app.models.tokens import AuthToken


@app.route('/api/buyers/', methods=['GET'])
def get_buyers():
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
            farmers_list = Buyer.query.all()
            return jsonify([farmer.to_dict() for farmer in farmers_list]), 200


@app.route('/api/buyer/<int:buyer_id>', methods=['GET'])
def get_buyer(buyer_id):
    """API ricezione elenco allevatori."""
    token = request.headers.get("token")
    if not token:
        return jsonify({"message": "Please log in."}), 401
    else:
        authenticated = AuthToken.query.filter(AuthToken.token == token).first()
        if authenticated in ["", None] or authenticated.expires_at < datetime.now():
            return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
        else:
            buyer = Buyer.query.filter_by(id=buyer_id).first()
            if buyer:
                if buyer.affiliation_start_date:
                    affiliation_start_date = datetime.strftime(buyer.affiliation_start_date, "%Y-%m-%d")
                else:
                    affiliation_start_date = buyer.affiliation_start_date

                if buyer.affiliation_end_date:
                    affiliation_end_date = datetime.strftime(buyer.affiliation_end_date, "%Y-%m-%d")
                else:
                    affiliation_end_date = buyer.affiliation_end_date

                return jsonify(
                    id=buyer.id,
                    buyer_name=buyer.buyer_name,
                    buyer_type=buyer.buyer_type,
                    email=buyer.email,
                    phone=buyer.phone,
                    user_id=buyer.user_id,
                    affiliation_start_date=affiliation_start_date,
                    affiliation_end_date=affiliation_end_date,
                    affiliation_status=buyer.affiliation_status,
                    address=buyer.address,
                    cap=buyer.cap,
                    city=buyer.city,
                    note=buyer.note,
                    created_at=datetime.strftime(buyer.created_at, "%Y-%m-%d %H:%M:%S"),
                    updated_at=datetime.strftime(buyer.updated_at, "%Y-%m-%d %H:%M:%S")
                ), 200
            else:
                return jsonify(error=f'Buyer not found with id: {buyer_id}'), 404
