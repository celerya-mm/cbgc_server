from datetime import datetime

from flask import request, jsonify, current_app as app

from app.models.heads import Head
from app.models.tokens import AuthToken


@app.route('/api/heads/', methods=['GET'])
def get_heads():
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
            heads_list = Head.query.all()
            return jsonify([head.to_dict() for head in heads_list]), 200


@app.route('/api/head/<int:head_id>', methods=['GET'])
def get_head(head_id):
    """API ricezione elenco allevatori."""
    token = request.headers.get("token")
    if not token:
        return jsonify({"message": "Please log in."}), 401
    else:
        authenticated = AuthToken.query.filter(AuthToken.token == token).first()
        if authenticated in ["", None] or authenticated.expires_at < datetime.now():
            return jsonify({"message": "You don't have a valid authentication token, please log in."}), 401
        else:
            head = Head.query.filter_by(id=head_id).first()
            if head:
                return jsonify(head.to_dict()), 200
            else:
                return jsonify(error=f'Head not found with id: {head_id}'), 404
