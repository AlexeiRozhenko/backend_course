import base64
import pytest
import datetime
from http import HTTPStatus
from fastapi.testclient import TestClient
from homework_4.demo_service.api.contracts import UserResponse
from homework_4.demo_service.api.main import create_app

app = create_app()
# pytest --cov=lecture_4 tests/lecture_4/hw/test_2.py

@pytest.fixture
def client():
    example = TestClient(app)
    with example as client:
        yield client

@pytest.fixture()
def user(client, password):
    username = 'userus'
    name = 'namus'
    birthdate = datetime.datetime(2025, 1, 1).isoformat()

    response = client.post('/user-register', 
        json = {
            'username': username,
            'name': name,
            'birthdate': birthdate,
            'password': password,
    })
    
    response_json = response.json()
    return UserResponse(
        uid = response_json['uid'], 
        username = username, 
        name = name, 
        birthdate = birthdate, 
        role = response_json['role']
    )

@pytest.fixture()
def password():
    return "29_05_1453"

@pytest.fixture()
def admin_credentials():
    return base64.b64encode(f"admin:superSecretAdminPassword123".encode("ascii")).decode("utf-8")


def test_register_ok(client, password):
    # arrange
    username = 'imposter'
    name = 'amogus'
    birthdate = datetime.datetime(2025, 1, 1).isoformat()

    # act
    response = client.post('/user-register', json = {
        'username': username,
        'name': name,
        'birthdate': birthdate,
        'password': password})
    response_json = response.json()

    # assert
    assert response.status_code == HTTPStatus.OK
    assert response_json['username'] == username
    assert response_json['birthdate'] == birthdate
    assert response_json['name'] == name


def test_register_error_repetition(client, user, password):
    # user тут как бы есть, но он не используется: он нужен, чтобы провести
    # операцию 1-й регистрации, чтобы затем протестировать 2-ю регистрацию
    # такое используется во многих тестах, хоть может этот user непосредственно и не нужОн
    username = 'userus'
    name = 'namus'
    birthdate = datetime.datetime(2025, 1, 1).isoformat()

    # arrange + act
    response_2 = client.post('/user-register', json={
        'username': username,
        'name': name,
        'birthdate': birthdate,
        'password': password,
    })

    # assert
    assert response_2.status_code == HTTPStatus.BAD_REQUEST


def test_register_error_wrong_pass(client):
    # arrange + act
    response = client.post('/user-register', json={
        'username': 'invalidus',
        'name': 'chromius',
        'birthdate': datetime.datetime(2025, 1, 1).isoformat(),
        'password': 'dummypass',
    })

    # assert
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_error_unknown(client, user, admin_credentials):
    # arrange + act
    response = client.post(
        "/user-get",
        params={'username': 'biba, boba brother'},
        headers={"Authorization": "Basic" + " " + admin_credentials},
    )
    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_error_username_id(client, user, admin_credentials):
    # arrange + act
    response = client.post("/user-get",
        params={'username': "upidy", 'id': 42},
        headers={"Authorization": "Basic" + " " + admin_credentials},
    )
    # assert
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_error_no_username_id(client, user, admin_credentials):
    # arrange + act
    response = client.post("/user-get",
        headers={"Authorization": "Basic" + " " + admin_credentials},
    )
    # assert
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_error_wrong_pass(client, user):
    # arrange
    credentials = base64.b64encode(f"admin:dummypass".encode("ascii")).decode("utf-8")
    # act
    response = client.post("/user-get",
        params={'id': 1},
        headers={"Authorization": "Basic" + " " + credentials},
    )
    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    

def test_get_id(client, user, admin_credentials):
    # arrange + act
    response = client.post("/user-get",
        params={'id': 2},
        headers={"Authorization": "Basic" + " " + admin_credentials},
    )
    response.json = response.json()
    # assert
    assert response.status_code == HTTPStatus.OK
    assert response.json['username'] == user.username
    assert response.json['uid'] == user.uid
    assert response.json['role'] == user.role


def test_promote(client, admin_credentials):
    # arrange + act
    response = client.post("/user-promote",
        params={'id': 1},
        headers={"Authorization": "Basic" + " " + admin_credentials}
    )
    # assert
    assert response.status_code == HTTPStatus.OK


def test_promote_error_not_admin(client, user, password):
    # arrange
    credentials = base64.b64encode(f"userus:{password}".encode("ascii")).decode("utf-8")
    # act
    response = client.post("/user-promote",
        params={'id': 1},
        headers={"Authorization": "Basic" + " " + credentials}
    )
    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_promote_error_no_user(client, admin_credentials):
    # arrange + act
    response = client.post("/user-promote",
        params={'id': 42},
        headers={"Authorization": "Basic" + " " + admin_credentials}
    )
    # assert
    assert response.status_code == HTTPStatus.BAD_REQUEST
