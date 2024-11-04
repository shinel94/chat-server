import json
import os
from datetime import datetime
from queue import Queue, Empty

from flask import Flask, jsonify, request, g, Response, render_template, send_from_directory
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker

from db.model import RoomType
from util.jwt_util import decode_jwt_token, create_jwt_token

from db.engine import engine
from db.user import get_user, add_user, check_password, exist_username, get_user_list as get_user_list_from_db
from db.chat import create_private_room, create_group_room, update_user_read_message_date, is_user_in_chatroom, \
    get_chatroom_detail, get_user_chatroom_list, get_open_chatroom_list, enter_room, get_user_count_in_room, leave_room
from db.message import add_chat_message_log, get_chat_message_log

app = Flask(__name__)
CORS(app)

chatroom_info = dict()
sessionmaker = sessionmaker(engine)


# 미들웨어 역할을 하는 before_request 훅
@app.before_request
def check_token():
    # 인증이 필요하지 않은 엔드포인트를 설정 (예: 로그인, 회원가입 등)
    open_endpoints = ['/', '/signin', '/signup']
    if request.path in open_endpoints or request.method == 'OPTIONS':
        return  # 인증이 필요 없는 엔드포인트는 통과
    if 'assets' in request.path:
        return
    if 'message_stream' in request.path:
        token = request.args.get('token')
        try:
            payload = decode_jwt_token(token)
            with sessionmaker() as session:
                g.user = get_user(session, payload['key'])
                return
        except:
            return jsonify({"error": "Unauthorized"}), 401
    # Authorization 헤더에서 토큰 추출
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]  # 'Bearer ' 이후의 실제 토큰 값 추출
        # 토큰 검증
        try:
            payload = decode_jwt_token(token)
            with sessionmaker() as session:
                g.user = get_user(session, payload['key'])
                return
        except:
            return jsonify({"error": "Unauthorized"}), 401

    # 토큰이 없거나 유효하지 않으면 401 응답
    return jsonify({"error": "Unauthorized"}), 401

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path.split('.')[-1] == 'js':
        return send_from_directory(app.static_folder, path, mimetype = 'text/javascript')
    return send_from_directory(app.static_folder, path)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    try:
        with sessionmaker() as session:
            if exist_username(session, username):
                return jsonify({"error": "Username already exists"}), 400
            add_user(session, username, password)
            user = get_user(session, username)
            user_id = user.id
        access_token = create_jwt_token(username)
        # 로그인 처리 로직
        return jsonify({"token": access_token, "user_id": user_id, "username": username})
    except:
        return jsonify({"error": "fail create user"}), 401

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    try:
        with sessionmaker() as session:
            user = check_password(session, username, password)
            if user is None:
                return jsonify({"error": "fail check user"}), 401
            access_token = create_jwt_token(username)
            # 로그인 처리 로직
            return jsonify({"token": access_token, "user_id": user.id, "username": user.username})
    except:
        return jsonify({"error": "fail signin"}), 401

@app.route('/users', methods=['GET'])
def get_user_list():
    try:
        with sessionmaker() as session:
            user_list = get_user_list_from_db(session)

            # 로그인 처리 로직
            return jsonify({"user_list": [
                {
                    "id": user.id,
                    "username": user.username
                } for user in user_list if user.id != g.user.id
            ]})
    except:
        return jsonify({"error": "fail get user list"}), 401


@app.route('/chatrooms', methods=['POST'])
def create_private_chatroom():
    data = request.json
    target_user_id_list = data.get('target_user_id_list')
    room_type = data.get('room_type')
    try:
        with sessionmaker() as session:
            if room_type == RoomType.PRIVATE:
                create_private_room(session, g.user.id, target_user_id_list[0])
            else:
                create_group_room(session, g.user.id, target_user_id_list)
        return Response("success", status=200)
    except:
        return jsonify({"error": "fail create private chatroom"}), 400


@app.route('/chatrooms', methods=['GET'])
def get_chatroom_list():
    try:
        with sessionmaker() as session:
            room_list = get_user_chatroom_list(session, g.user.id)
            open_room_list = get_open_chatroom_list(session)
            return jsonify({
                "entered_chatroom_list": [
                    {
                        "chatroom_id": row[0].chatroom_id,
                        "last_message_date": row[2],
                        "read_message_date": row[0].last_read_message_date,
                        "room_type": row[1]
                    } for row in room_list
                ],
                "open_chatroom_list": [
                    {
                        "chatroom_id": row[0].id,
                        "last_message_date": row[1],
                        "active_user_count": row[2],
                        "room_type": row[0].room_type
                    } for row in open_room_list
                ]
            })
    except:
        return jsonify({"error": "fail get chatroom list"}), 400

@app.route('/chatrooms/<chatroom_id>', methods=['POST'])
def post_enter_chatroom(chatroom_id: int):
    chatroom_id = int(chatroom_id)
    try:
        with sessionmaker() as session:
            if not is_user_in_chatroom(session, g.user.id, chatroom_id) and get_user_count_in_room(session, chatroom_id) < 100:
                enter_room(session, g.user.id, chatroom_id)
                chatroom_detail = get_chatroom_detail(session, chatroom_id)
                return jsonify({
                    "chatroom_id": chatroom_detail['chatroom'].id,
                    "chatroom_name": chatroom_detail['chatroom'].name,
                    "user_list": [
                        {
                            "id": row[0].id,
                            "username": row[0].username,
                            "last_message_date": row[1]
                        } for row in chatroom_detail['user_list']
                    ]
                })
            else:
                return jsonify({"error": "fail get chatroom info"}), 400
    except:
        return jsonify({"error": "fail get chatroom info"}), 400


@app.route('/chatrooms/<chatroom_id>', methods=['DELETE'])
def post_leave_chatroom(chatroom_id: int):
    chatroom_id = int(chatroom_id)
    try:
        with sessionmaker() as session:
            if is_user_in_chatroom(session, g.user.id, chatroom_id):
                leave_room(session, g.user.id, chatroom_id)
                return Response(status=201)
            else:
                return jsonify({"error": "fail get chatroom info"}), 400
    except:
        return jsonify({"error": "fail get chatroom info"}), 400


@app.route('/chatrooms/<chatroom_id>', methods=['GET'])
def get_chatroom_info(chatroom_id: int):
    chatroom_id = int(chatroom_id)
    try:
        with sessionmaker() as session:
            if is_user_in_chatroom(session, g.user.id, chatroom_id):
                chatroom_detail = get_chatroom_detail(session, chatroom_id)
                return jsonify({
                    "chatroom_id": chatroom_detail['chatroom'].id,
                    "chatroom_name": chatroom_detail['chatroom'].name,
                    "user_list": [
                        {
                            "id": row[0].id,
                            "username": row[0].username,
                            "last_message_date": row[1]
                        } for row in chatroom_detail['user_list']
                    ]
                })
            else:
                return jsonify({"error": "fail get chatroom info"}), 400
    except:
        return jsonify({"error": "fail get chatroom info"}), 400


@app.route('/chatrooms/<chatroom_id>/message', methods=['GET'])
def get_chatroom_message(chatroom_id: int):
    chatroom_id = int(chatroom_id)
    last_message_date = request.args.get('last_message_date', default=None, type=datetime)  # 마지막 메세지의 날짜
    limit = request.args.get('limit', default=10, type=int)  # 'limit' 파라미터, 기본값 10

    try:
        with sessionmaker() as session:
            message_list = [
                {
                    "message_date": message.created_at,
                    "send_user_id": message.user_id,
                    "message_content": message.message,
                } for message in
                get_chat_message_log(session, chatroom_id, last_message_date, limit)
            ]
            if last_message_date is None and len(message_list) > 0:
                update_user_read_message_date(session, g.user.id, chatroom_id, message_list[0]['message_date'])

        return jsonify({"message_list": message_list[::-1]})
    except:
        return jsonify({"error": "fail get chatroom message"}), 400

@app.route('/chatrooms/<chatroom_id>/message', methods=['POST'])
def post_chatroom_message(chatroom_id: int):
    chatroom_id = int(chatroom_id)
    data = request.json
    content = data.get('content')

    try:
        with sessionmaker() as session:
            chat_log = add_chat_message_log(session, g.user.id, chatroom_id, content)

            payload = {
                "send_user_id": chat_log.user_id,
                "message_date": chat_log.created_at,
                "message_content": chat_log.message
            }
        try:
            message_queue_list = chatroom_info[chatroom_id]
        except KeyError:
            return jsonify({"error": "subscriber is not exist"}), 400
        for message_queue in message_queue_list.values():
            message_queue.put(payload)

        return Response("success", status=200)
    except:
        return jsonify({"error": "fail send chatroom message"}), 400

@app.route('/message_stream/<room_id>')
def message_stream(room_id):
    room_id = int(room_id)
    key = request.args.get('key', type=str)
    user_id = g.user.id
    session_key = f'{key}-{user_id}'
    def stream():
        print('read start')

        try:
            message_queue: Queue = chatroom_info[room_id][session_key]
        except KeyError:
            try:
                room_queue_map = chatroom_info[room_id]
            except KeyError:
                chatroom_info[room_id] = dict()
                room_queue_map = chatroom_info[room_id]
            room_queue_map[session_key] = Queue()
            message_queue: Queue = chatroom_info[room_id][session_key]

        read_message_date = None
        while True:
            try:
                content = message_queue.get()
                read_message_date = content['message_date']
                yield f'data: {json.dumps({
                    **content,
                    "message_date": content['message_date'].isoformat()
                })}\n\n'
            except GeneratorExit:
                if read_message_date is not None:
                    with sessionmaker() as session:
                        update_user_read_message_date(session, user_id, room_id, read_message_date)
                chatroom_info[room_id].pop(session_key)
                print(f'key info {list(chatroom_info[room_id].keys())}')
                if len(chatroom_info[room_id].keys()) == 0:
                    chatroom_info.pop(room_id)

    return Response(stream(), mimetype="text/event-stream")

# 서버 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)