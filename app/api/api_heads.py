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
            farmers_list = Head.query.all()
            return jsonify([farmer.to_dict() for farmer in farmers_list]), 200


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
                if head.bird_date:
                    bird_date = datetime.strftime(head.bird_date, "%Y-%m-%d")
                else:
                    bird_date = head.bird_date

                if head.castration_date:
                    castration_date = datetime.strftime(head.castration_date, "%Y-%m-%d")
                else:
                    castration_date = head.castration_date

                if head.slaughter_date:
                    slaughter_date = datetime.strftime(head.slaughter_date, "%Y-%m-%d")
                else:
                    slaughter_date = head.slaughter_date

                if head.sale_date:
                    sale_date = datetime.strftime(head.sale_date, "%Y-%m-%d")
                else:
                    sale_date = head.sale_date

                return jsonify(
                    id=head.id,
                    headset=head.headset,
                    bird_date=bird_date,
                    castration_date=castration_date,
                    castration_compliance=head.castration_compliance,
                    slaughter_date=slaughter_date,
                    sale_date=sale_date,
                    sale_year=head.sale_year,
                    note=head.note,
                    created_at=datetime.strftime(head.created_at, "%Y-%m-%d %H:%M:%S"),
                    updated_at=datetime.strftime(head.updated_at, "%Y-%m-%d %H:%M:%S")
                ), 200
            else:
                return jsonify(error=f'Head not found with id: {head_id}'), 404
