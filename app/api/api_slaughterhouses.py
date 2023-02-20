from datetime import datetime

from flask import request, jsonify, current_app as app

from app.models.slaughterhouses import Slaughterhouse
from app.models.auth_tokens import AuthToken


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
            slaughterhouses_list = Slaughterhouse.query.all()
            return jsonify([slaughterhouse.to_dict() for slaughterhouse in slaughterhouses_list]), 200


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
                return jsonify(slaughterhouse.to_dict()), 200
            else:
                return jsonify(error=f'Slaughterhouse not found with id: {slaughterhouse_id}'), 404
