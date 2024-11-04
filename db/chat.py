from sqlalchemy import func, exists
from sqlalchemy.orm.session import Session
from db.model import Chatroom, UserChatroom, RoomType, UserChatLog, User
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
        active_user_count = session.query(UserChatroom).filter_by(chatroom_id=room_id, is_active=True).count()
        if active_user_count == 1:
            chat_room = session.query(Chatroom).filter_by(id=room_id).first()
            chat_room.is_active = False
        user = session.query(UserChatroom).filter_by(user_id=user_id, chatroom_id=room_id, is_active=True).first()
        user.is_active = False
        session.commit()
    except Exception as e:
        raise e

def is_user_in_chatroom(session: Session, user_id, room_id):
    return session.query(exists().where(UserChatroom.user_id == user_id, UserChatroom.chatroom_id==room_id, UserChatroom.is_active==True )).scalar()

def create_private_room(session: Session, user_id, tar_user_id):
    room_name = f'p-${user_id}-${tar_user_id}'
    try:
        room = create_room(session, room_name, RoomType.PRIVATE)
        enter_room(session, user_id, room.id)
        enter_room(session, tar_user_id, room.id)
    except Exception as e:
        raise e
    return room

def create_group_room(session: Session, create_user_id, tar_user_id_list):
    room_name = f'g-${create_user_id}-${datetime.now().strftime("%Y%m%d%H%M%S")}'
    try:
        room = create_room(session, room_name, RoomType.GROUP)
        enter_room(session, create_user_id, room.id)
        for tar_user_id in tar_user_id_list:
            enter_room(session, tar_user_id, room.id)
    except Exception as e:
        raise e
    return room

def get_user_chatroom_list(session: Session, user_id):

    return session.query(
        UserChatroom,
        func.max(UserChatLog.created_at).label('messaging_time')
    ).select_from(UserChatroom).filter_by(
        user_id=user_id, is_active=True
    ).join(Chatroom).outerjoin(UserChatLog).group_by(
        UserChatroom.chatroom_id
    ).order_by(
        func.max(UserChatLog.created_at).desc()
    ).all()

def get_open_chatroom_list(session: Session):
    return session.query(
        Chatroom,
        func.max(UserChatLog.created_at).label('messaging_time'),
        func.count(UserChatroom.user_id.distinct()).label('active_user_count')
    ).filter(
        Chatroom.room_type==RoomType.GROUP, Chatroom.is_active==True, UserChatroom.is_active==True
    ).outerjoin(UserChatroom).outerjoin(UserChatLog).group_by(
        Chatroom.id,
    ).order_by(
        func.max(UserChatLog.created_at).desc()
    ).all()

def get_chatroom_detail(session: Session, room_id):
    chatroom = session.query(Chatroom).filter_by(id=room_id).one_or_none()
    user_list = session.query(UserChatroom).filter_by(chatroom_id=room_id, is_active=True).join(User).all()
    return {
        'chatroom': chatroom,
        'user_list': user_list
    }

def get_user_count_in_room(session: Session, room_id):
    return session.query(UserChatroom).filter_by(chatroom_id=room_id, is_active=True).count()

def update_user_read_message_date(session: Session, user_id, room_id, read_message_date):
    try:
        user_chatroom = session.query(UserChatroom).filter_by(user_id=user_id, chatroom_id=room_id, is_active=True).one_or_none()
        user_chatroom.last_read_message_date = read_message_date
        session.commit()
    except Exception as e:
        raise e


if __name__ == "__main__":
    from db.user import add_user, get_user
    from db.engine import engine

    session = Session(engine)
    # user1 = add_user(session,'test1', 'test1pwd')
    user1 = get_user(session, 'test1')
    # user2 = add_user(session,'test2', 'test2pwd')

    # create_private_room(session, user1.id, user2.id)
    #
    # user_list = [add_user(session, f'many-user-{i:03}', f'many-user-pwd-{i:03}') for i in range(5)]
    #
    # create_group_room(session, user1.id, [u.id for u in user_list])

    print([[r[0].chatroom.name, r[0].chatroom_id, r[0].last_read_message_date, r[1]] for r in get_user_chatroom_list(session, user1.id)])