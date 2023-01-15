from datetime import datetime

from flask import request, jsonify, current_app as app

from app.models.buyers import Buyer
from app.models.tokens import AuthToken


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
            buyer_list = Buyer.query.all()
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
            buyer = Buyer.query.filter_by(id=buyer_id).first()
            if buyer:
                return jsonify(buyer.to_dict()), 200
            else:
                return jsonify(error=f'Buyer not found with id: {buyer_id}'), 404
