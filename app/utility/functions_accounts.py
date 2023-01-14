import random
import string
from datetime import datetime, timedelta

from email_validator import validate_email, EmailNotValidError

from app.app import db
from app.models.tokens import AuthToken


def __generate_auth_token():
    """Genero random token."""
    return ''.join([random.choice(string.ascii_letters + string.digits) for _n in range(64)])


def __save_auth_token(admin_id, user_id, token):
    """Salvo il token nel DB."""
    if admin_id in [""]:
        admin_id = None
    if user_id in [""]:
        user_id = None
    DATETIME = datetime.now()
    EXPIRATION = datetime.now() + timedelta(days=1)
    EXPIRATION = EXPIRATION.replace(hour=0, minute=0, second=0, microsecond=0)
    auth_token = AuthToken(
        admin_id=admin_id,
        user_id=user_id,
        token=token,
        expires_at=EXPIRATION
    )
    db.session.add(auth_token)
    db.session.commit()
    return auth_token


def is_valid_email(_email):
    try:
        v = validate_email(_email)
        print(v)
        return True
    except EmailNotValidError:
        return False
