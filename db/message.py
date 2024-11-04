from datetime import datetime

from sqlalchemy.orm.session import Session
from db.model import UserChatLog
from db.util import insert_data

def get_chat_message_log(session: Session, room_id, last_search_date:datetime=None, limit=10):
    query = session.query(UserChatLog).filter_by(chatroom_id=room_id)
    if last_search_date is not None:
        query = query.filter(UserChatLog.created_at < last_search_date)
    return query.order_by(UserChatLog.created_at.desc()).limit(limit).all()

def add_chat_message_log(session: Session, user_id, room_id, message_content):
    user_chat_log = UserChatLog(user_id=user_id, chatroom_id=room_id, message=message_content)
    try:
        insert_data(session, user_chat_log)
    except Exception as e:
        raise e
    return user_chat_log


if __name__ == "__main__":
    from db.user import add_user
    from db.chat import create_private_room
    from db.engine import engine

    session = Session(engine)
    # user1 = add_user(session,'message_test1', 'test1pwd')
    # user2 = add_user(session,'message_test2', 'test2pwd')
    #
    # room = create_private_room(session, user1.id, user2.id)
    #
    # for i in range(100):
    #     message = add_chat_message_log(session, user1.id, room.id, f"message-{i}")

    message = get_chat_message_log(session, 3)
    print(message)
    print([m.message for m in message])

    while len(message) > 0:
        print(message)
        print([m.message for m in message])
        message = get_chat_message_log(session, 3, message[-1].created_at)

    print(message)