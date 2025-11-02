import pytest
import requests

from tests.commons.request_util import RequestUtil


class TestSession:

    csrf_token = ''

    def test_user_register(self):
        url = 'http://127.0.0.1:8000/auth/users/'
        data = {
            'username': 'testuser',
            'password': '0123456789*',
            'email': 'testuser@123.com',
        }
        res = RequestUtil().all_send_request(method='post',url=url, json=data)

    def test_user_login(self):
        url = 'http://127.0.0.1:8000/auth/jwt/create'
        data = {
            'username': 'admin',
            'password': '123456',
        }
        res = RequestUtil().all_send_request(method='post', url=url, json=data)

