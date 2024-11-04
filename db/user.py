from bcrypt import hashpw, checkpw, gensalt
from sqlalchemy import exists
from sqlalchemy.orm.session import Session

from db.model import User
from db.util import insert_data
HASH_SECRET_KEY = "a20xjmqh1ic4vl91"

def get_user(session: Session, username):
    return session.query(User).filter_by(username=username).one_or_none()

def add_user(session: Session, username, password):
    hashed_pw = hashpw(f'{HASH_SECRET_KEY}{password}'.encode('utf-8'), gensalt())
    user = User(username=username, password=hashed_pw.decode('utf-8'))
    try:
        insert_data(session, user)
    except Exception as e:
        raise e

    return user

def exist_username(session:Session, username):
    return session.query(exists().where(User.username == username)).scalar()

def check_password(session: Session, username, password):
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        return user

    if checkpw(f'{HASH_SECRET_KEY}{password}'.encode(), user.password.encode('utf-8')):
        return user
    else:
        return None

if __name__ == "__main__":
    from db.engine import engine

    session = Session(engine)
    add_user(session, 'test', 'testpwd')
    check_password(session, 'test', 'testpwd')