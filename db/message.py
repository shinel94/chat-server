from sqlalchemy.orm.session import Session
from db.model import UserChatLog
from db.util import insert_data

def add_message_log(session: Session):
    pass

def get_chat_message_log(session: Session, room_id):
    session.query(UserChatLog).filter_by(room_id=room_id).order_by('-created_at')
    pass

def add_chat_message_log(session: Session, user_id, room_id, message_content):
    user_chat_log = UserChatLog(user_id=user_id, chatroom_id=room_id, message=message_content)
    try:
        insert_data(session, user_chat_log)
    except Exception as e:
        raise e
    return user_chat_log
