import secrets, hashlib, datetime as dt
from database.main import Database

def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def create_session(user_id: int, days: int = 1):
    """Create a new session and return brute hash"""
    raw = secrets.token_urlsafe(32)
    h = _hash_token(raw)
    expires_at = dt.datetime.now() + dt.timedelta(days=days)

    db = Database()
    # metoda ta DB trebuie să facă INSERT în tabelul sessions
    db.create_session(user_id, h, expires_at)

    return raw, expires_at


def validate_session(sid: str):
    try:
        if sid:
            hash_sid = _hash_token(sid)

            database = Database()
            validate_response = database.validate_session(hash_sid)
            if validate_response['status'] == 302:
                return validate_response['data']['user_id']
            else:
                return False
        else:
            return False
    except Exception as error:
        print(error)
        return True


def remove_session_id(sid: str):
    try:
        if sid:
            hash_sid = _hash_token(sid)
            database = Database()
            database.delete_session(hash_sid)

        else:
            pass
    except Exception as error:
        print(error)