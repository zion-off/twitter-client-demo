import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class NetworkRequest:
    @staticmethod
    def get(url, headers={}):
        req = Request(url=url, method="GET")
        for key, value in headers.items():
            req.add_header(key, value)

        result = {}
        with urlopen(req) as res:
            body = res.read().decode("utf-8")
            result["body"] = json.loads(body)
            result["code"] = res.status

        return result

    @staticmethod
    def post(url, headers={}, data={}):
        req = Request(url=url, method="POST", data=json.dumps(data).encode("utf-8"))
        for key, value in headers.items():
            req.add_header(key, value)

        result = {}
        try:
            with urlopen(req) as res:
                body = res.read().decode("utf-8")
                result["body"] = json.loads(body)
                result["code"] = res.status
        except HTTPError as e:
            result["body"] = e.read().decode("utf-8")
            result["code"] = e.code
            result["reason"] = e.reason

        return result

    @staticmethod
    def put():
        pass

    @staticmethod
    def delete():
        pass


class Authentication:
    def __init__(self):
        self.accessToken = None
        self.refreshToken = None

    def register(self):
        firstName = input("Enter your first name: ")
        lastName = input("Enter your last name: ")
        username = input("Enter a username: ")
        password = input("Enter a password: ")
        data = {
            "username": username,
            "firstname": firstName,
            "lastname": lastName,
            "password": password,
        }
        headers = {}
        headers["Content-Type"] = "application/json"
        res = NetworkRequest.post(
            "http://localhost:8000/api/users", headers=headers, data=data
        )
        if res["code"] == 200:
            print("Registration successful.")
        else:
            if res["reason"]:
                print(res["reason"], end="")
            print(". Try again.")

    def login(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        data = {"username": username, "password": password}
        headers = {}
        headers["Content-Type"] = "application/json"
        res = NetworkRequest.post("http://localhost:8000/api/auth", headers, data=data)
        if res["code"] == 200:
            self.accessToken = res["body"].get("access_token")
            self.refreshToken = res["body"].get("refresh_token")
            print("Login successful.")
        else:
            if res["reason"]:
                print(res["reason"], end="")
            print(". Try again.")
