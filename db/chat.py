from sqlalchemy import func
from sqlalchemy.orm.session import Session
from db.model import Chatroom, UserChatroom, RoomType, UserChatLog
from db.util import insert_data
from datetime import datetime

def create_room(session: Session, name, room_type):
    chat_room = Chatroom(name=name, room_type=room_type)
    try:
        insert_data(session, chat_room)
    except Exception as e:
        raise e
    return chat_room

def enter_room(session: Session, user_id, room_id):
    user_chat_room = UserChatroom(user_id=user_id, chatroom_id=room_id)
    try:
        insert_data(session, user_chat_room)
    except Exception as e:
        raise e
    return user_chat_room

def leave_room(session: Session, user_id, room_id):
    try:
        active_user_count = session.query(UserChatroom).filter_by(user_id=user_id, chatroom_id=room_id, is_active=True).count()
        if active_user_count == 1:
            chat_room = session.query(Chatroom).filter_by(id=room_id).first()
            chat_room.is_active = False
        user = session.query(UserChatroom).filter_by(user_id=user_id, chatroom_id=room_id, is_active=True).first()
        user.is_active = False
        session.commit()
    except Exception as e:
        raise e

def get_user_count_in_room(session: Session, room_id):
    return session.query(UserChatroom).filter_by(chatroom_id=room_id, is_active=True).count()

def create_private_room(session: Session, user_id, tar_user_id):
    room_name = f'p-${user_id}-${tar_user_id}'
    try:
        room = create_room(session, room_name, RoomType.PRIVATE)
        enter_room(session, user_id, room.id)
        enter_room(session, tar_user_id, room.id)
    except Exception as e:
        raise e

def create_group_room(session: Session, create_user_id, tar_user_id_list):
    room_name = f'g-${create_user_id}-${datetime.now().strftime("%Y%m%d%H%M%S")}'
    try:
        room = create_room(session, room_name, RoomType.GROUP)
        enter_room(session, create_user_id, room.id)
        for tar_user_id in tar_user_id_list:
            enter_room(session, tar_user_id, room.id)
    except Exception as e:
        raise e

def get_user_room_list(session: Session, user_id):

    return session.query(
        UserChatroom
    ).filter_by(
        user_id=user_id, is_active=True
    ).join(Chatroom).outerjoin(UserChatLog).group_by(
        UserChatroom.chatroom_id
    ).order_by(
        func.max(UserChatLog.created_at).label('messaging_time').desc()
    ).all()


if __name__ == "__main__":
    from db.user import add_user, get_user
    from db.engine import engine

    session = Session(engine)
    # user1 = add_user(session,'test1', 'test1pwd')
    user1 = get_user(session, 'test1')
    # user2 = add_user(session,'test2', 'test2pwd')

    # create_private_room(session, user1.id, user2.id)

    # user_list = [add_user(session, f'many-user-{i:03}', f'many-user-pwd-{i:03}') for i in range(5)]

    # create_group_room(session, user1.id, [u.id for u in user_list])

    print([[r.chatroom.name, r.chatroom_id] for r in get_user_room_list(session, user1.id)])