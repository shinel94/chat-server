from datetime import datetime
from queue import Queue

from flask import Flask, jsonify, request, g, Response
from sqlalchemy.orm import sessionmaker

from util.jwt_util import decode_jwt_token, create_jwt_token

from db.engine import engine
from db.user import get_user, add_user, check_password, exist_username
from db.message import add_chat_message_log

app = Flask(__name__)

chatroom_info = dict()
sessionmaker = sessionmaker(engine)


# 미들웨어 역할을 하는 before_request 훅
@app.before_request
def check_token():
    # 인증이 필요하지 않은 엔드포인트를 설정 (예: 로그인, 회원가입 등)
    open_endpoints = ['/signin', '/signup']
    if request.path in open_endpoints:
        return  # 인증이 필요 없는 엔드포인트는 통과

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
        access_token = create_jwt_token(username)
        # 로그인 처리 로직
        return jsonify({"token": access_token})
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
            return jsonify({"token": access_token})
    except:
        return jsonify({"error": "fail signin"}), 401


@app.route('/chatrooms', methods=['GET'])
def get_chatroom_list():
    try:
        with sessionmaker() as session:
            return jsonify({
                "chatroom_list": [
                    {
                        "chatroom_id": -1,
                        "last_message_date": datetime.now(),
                    }
                ]
            })
    except:
        return jsonify({"error": "fail signin"}), 401

@app.route('/chatrooms/<chatroom_id>', methods=['GET'])
def get_chatroom_info(chatroom_id: int):
    try:
        with sessionmaker() as session:
            return jsonify({
                "chatroom_id": -1,
                "chatroom_name": "",
                "user_list": []
            })
    except:
        return jsonify({"error": "fail signin"}), 401


@app.route('/chatrooms/<chatroom_id>/message', methods=['GET'])
def get_chatroom_message(chatroom_id: int):
    last_message_date = request.args.get('last_message_date', type=datetime)  # 마지막 메세지의 날짜
    limit = request.args.get('limit', default=10, type=int)  # 'limit' 파라미터, 기본값 10

    try:
        with sessionmaker() as session:
            return jsonify({"message_list": [
                {
                    "message_date": datetime.now(),
                    "send_user_id": -1,
                    "message_content": ""
                }
            ]})
    except:
        return jsonify({"error": "fail signin"}), 401



@app.route('/chatrooms/<chatroom_id>/message', methods=['POST'])
def post_chatroom_message(chatroom_id: int):
    data = request.json
    content = data.get('content')

    try:
        with sessionmaker() as session:
            chat_log = add_chat_message_log(session, g.user.id, chatroom_info, content)

        payload = {
            "send_user_id": chat_log.user_id,
            "message_date": chat_log.created_at,
            "message_content": chat_log.content
        }
        try:
            message_queue = chatroom_info[chatroom_id][0]
        except KeyError:
            return jsonify({"error": "fail send message"}), 400

        message_queue.append(payload)

        return Response("success", status=200)
    except:
        return jsonify({"error": "fail signin"}), 401



@app.route('/message_stream/<room_id>')
def message_stream(room_id):
    user_id = g.user.id
    def stream():
        try:
            message_queue: Queue = chatroom_info[room_id][0]
        except KeyError:
            chatroom_info[room_id] = (Queue(), [])
            message_queue: Queue = chatroom_info[room_id][0]

        stream_user_list = chatroom_info[room_id][1]
        stream_user_list.append(user_id)
        while True:
            try:
                content = message_queue.get()
                yield f'{content}'
            except GeneratorExit:
                stream_user_list.pop(stream_user_list.index(user_id))
                if len(stream_user_list) == 0:
                    chatroom_info.pop(room_id)

    return Response(stream(), mimetype="text/event-stream")

# 서버 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)