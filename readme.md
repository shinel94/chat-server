# 채팅 시스템 과제

## 프로젝트 개요
프로젝트는 과제를 위해 개발된 간단한 채팅 시스템이고, **Python 3.12.6**과 **Flask 3.0.3**을 사용하여 구축되었으며, **SQLite**를 데이터베이스 활용하고 있어 추가적인 db 연결 없이도 쉽게 사용할 수 있습니다.

## 요구 사항
프로젝트를 실행하려면 필요한 Python 패키지를 설치해야 합니다. 이러한 패키지는 프로젝트 루트에 있는 `requirements.txt` 파일에 나열되어 있으며, 다음 명령어를 사용하여 설치할 수 있습니다:

```sh
pip install -r requirements.txt
```

## 프로젝트 실행
종속성을 설치한 후, 프로젝트 루트 디렉터리에 있는 `main.py` 스크립트를 실행하여 서버를 시작할 수 있습니다:

```sh
python main.py
```

기본적으로 서버는 **0.0.0.0**의 **8000**번 포트에서 호스팅됩니다. 웹 브라우저에서 **127.0.0.1:8000**으로 접속하여 채팅 시스템의 데모 클라이언트를 사용할 수 있습니다.

## 문서
프로젝트에는 시스템의 아키텍처와 흐름을 이해하는 데 도움이 되는 여러 문서 파일이 포함되어 있습니다:

- [**엔터티-관계 다이어그램 (ERD)**](docs/erd.md): `docs/erd.md`에 있으며, 채팅 시스템에서 사용되는 데이터베이스 구조를 설명합니다.
- [**사용자 흐름도**](docs/flow-chart.md): 시스템과의 사용자 상호작용 흐름이 `docs/flow-chart.md`에 나와 있습니다.
- [**API 명세서**](docs/api.md): API에 대한 자세한 정보는 `docs/api.md`에서 확인할 수 있습니다.

## 주요 기능
- **사용자 등록 및 인증**
- **채팅방 생성 및 관리**
- **실시간 메시징** (Server-Sent Events, SSE 사용)

## 기술 스택
- **Python 3.12.6**: 서버 측 로직에 사용된 주요 프로그래밍 언어.
- **Flask 3.0.3**: API 빌드 및 HTTP 요청 처리를 위한 경량 웹 프레임워크.
- **SQLite**: 경량의 서버리스, 자체 포함형 SQL 데이터베이스 엔진으로 지속적인 데이터 저장에 사용됩니다.

## 라이선스
이 프로젝트는 교육 목적으로 제공되며 상업적 사용에 대한 라이선스는 제공되지 않습니다.

## 도움 받기
프로젝트 실행 중 문제가 발생하거나 구현에 대한 질문이 있는 경우, 저장소에 이슈를 열어주시면 됩니다.

## 기여하기
이 프로젝트는 간단한 과제용 프로젝트이지만, 기여는 언제나 환영합니다. 저장소를 포크하고 개선 사항이나 새로운 기능을 추가하고 싶다면 풀 리퀘스트를 제출해 주세요.
