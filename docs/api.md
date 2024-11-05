# API Documentation

## Authentication APIs

### 1. Sign Up API
- **Endpoint**: `/signup`
- **Method**: POST
- **Request Body**: 
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
  - Content-Type: `application/json`
- **Responses**:
  - **200 OK**: 
    ```json
    {
      "token": "string",
      "user_id": "int",
      "username": "string"
    }
    ```
  - **400 Bad Request**: Username already exists.

### 2. Sign In API
- **Endpoint**: `/signin`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
  - Content-Type: `application/json`
- **Responses**:
  - **200 OK**:
    ```json
    {
      "token": "string",
      "user_id": "int",
      "username": "string"
    }
    ```
  - **401 Unauthorized**: Password is incorrect.

## Authorized APIs (Require JWT Authorization Header)

### 3. User List API
- **Endpoint**: `/users`
- **Method**: GET
- **Responses**:
  - **200 OK**:
    ```json
    [
      {
        "id": "int",
        "username": "string"
      }
    ]
    ```
  - **400 Bad Request**: Error message.

### 4. Create Chatroom API
- **Endpoint**: `/chatrooms`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "room_type": 100|200,
    "target_user_id_list": ["int"]
  }
  ```
  - Content-Type: `application/json`
- **Responses**:
  - **200 OK**: "success"
  - **400 Bad Request**: Error message.

### 5. Get Chatrooms API
- **Endpoint**: `/chatrooms`
- **Method**: GET
- **Responses**:
  - **200 OK**:
    ```json
    {
      "entered_chatroom_list": [
        {
          "chatroom_id": "number",
          "last_message_date": "date",
          "read_message_date": "date",
          "room_type": 100|200
        }
      ],
      "open_chatroom_list": [
        {
          "chatroom_id": "number",
          "last_message_date": "date",
          "active_user_count": "number",
          "room_type": 100|200
        }
      ]
    }
    ```
  - **400 Bad Request**: Error message.

### 6. Join Chatroom API
- **Endpoint**: `/chatrooms/<chatroom_id>`
- **Method**: POST
- **Responses**:
  - **200 OK**:
    ```json
    {
      "chatroom_id": "int",
      "chatroom_name": "string",
      "user_list": [
        {
          "id": "int",
          "username": "string",
          "last_message_date": "date"
        }
      ]
    }
    ```
  - **400 Bad Request**: Error message.

### 7. Leave Chatroom API
- **Endpoint**: `/chatrooms/<chatroom_id>`
- **Method**: DELETE
- **Responses**:
  - **200 OK**: No content.
  - **400 Bad Request**: Error message.

### 8. Get Chatroom Details API
- **Endpoint**: `/chatrooms/<chatroom_id>`
- **Method**: GET
- **Responses**:
  - **200 OK**:
    ```json
    {
      "chatroom_id": "int",
      "chatroom_name": "string",
      "user_list": [
        {
          "id": "int",
          "username": "string",
          "last_message_date": "date"
        }
      ]
    }
    ```
  - **400 Bad Request**: Error message.

### 9. Get Chatroom Messages API
- **Endpoint**: `/chatrooms/<chatroom_id>/message`
- **Method**: GET
- **Query Parameters**:
  - `last_message_date` (optional): `datetime`
  - `limit` (optional): `int`
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message_list": [
        {
          "message_date": "datetime",
          "send_user_id": "int",
          "message_content": "string"
        }
      ]
    }
    ```
  - **400 Bad Request**: Error message.

### 10. Send Message in Chatroom API
- **Endpoint**: `/chatrooms/<chatroom_id>/message`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "content": "string"
  }
  ```
  - Content-Type: `application/json`
- **Responses**:
  - **200 OK**: "success"
  - **400 Bad Request**: Error message.

### 11. Real-time Chat Message Stream API (Server-Sent Events)
- **Endpoint**: `/message_stream/<room_id>`
- **Query Parameters**:
  - `token`: `string`
  - `key`: `string`
- **Streamed Data**:
  ```json
  {
    "message_date": "datetime",
    "send_user_id": "int",
    "message_content": "string"
  }
  