import json
from time import sleep
from pyjokes import get_joke
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class NetworkRequest:
    @staticmethod
    def get(url, headers={}, params=None):
        if params:
            query_string = urlencode(params)
        url = url + query_string
        req = Request(url=url, method="GET")
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
        self.currentUser = None
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
            self.currentUser = username
            self.accessToken = res["body"].get("access_token")
            self.refreshToken = res["body"].get("refresh_token")
            print("Login successful.")
        else:
            if res["reason"]:
                print(res["reason"], end="")
            print(". Try again.")


class Twitter:
    def __init__(self):
        self.usedTweets = set()

    def generator(self, n):
        value = 0
        while value < n:
            joke = get_joke()
            while joke in self.usedTweets:
                joke = get_joke()
            yield joke
            self.usedTweets.add(joke)
            value += 1

    def getRecentTweets(self, auth):
        print("Checking recent tweets...")
        params = {"limit": 5, "skip": 0}
        headers = {"Authorization": f"Bearer {auth.accessToken}"}
        res = NetworkRequest.get(
            "http://localhost:8000/api/tweets?", headers=headers, params=params
        )
        if res["code"] == 200:
            for tweet in res["body"]:
                print(tweet["author"]["username"], " tweeted at ", tweet["created_at"])
                print(tweet["text"])
                print()

        else:
            if res["reason"]:
                print("Could not get tweets!", end=" ")
                print(res["reason"], end=".")

    def postTweets(self, auth):
        print("Posting tweets...")

        for value in self.generator(10):
            tweet = {
                "text": value,
            }
            headers = {}
            headers["Content-Type"] = "application/json"
            headers["Authorization"] = f"Bearer {auth.accessToken}"
            res = NetworkRequest.post(
                "http://localhost:8000/api/tweets", headers=headers, data=tweet
            )
            if res["code"] == 201:
                print(value)
                print("Posted 1 tweet. Sleeping for 1 minute now.")
                sleep(3)
            else:
                if res["reason"]:
                    print("Could not post this tweet!", end=" ")
                    print(res["reason"], end=".")
