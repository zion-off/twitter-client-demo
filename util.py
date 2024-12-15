import json
import time
from pyjokes import get_joke
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def logger(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print(f"Time taken: {end - start}\n")
        with open("log.txt", "a") as myfile:
            myfile.write(f"Time taken: {end - start}\n")

    return wrapper


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

    @logger
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
            with open("log.txt", "a") as myfile:
                myfile.write("Registration successful.")
        else:
            if res["reason"]:
                print(res["reason"], ". Try again.")
                with open("log.txt", "a") as myfile:
                    myfile.write(res["reason"], ". Try again.")

    @logger
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
            with open("log.txt", "a") as myfile:
                myfile.write("Login successful. ")
        else:
            if res["reason"]:
                print(res["reason"], ". Try again.")
                with open("log.txt", "a") as myfile:
                    myfile.write(res["reason"], ". Try again.")

    @staticmethod
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            if res["code"] == 401:
                print("Trying to reauthenticate...")
                with open("log.txt", "a") as myfile:
                    myfile.write("Trying to reauthenticate...")
                auth = kwargs.get("auth")
                if auth:
                    data = {"refresh_token": auth.refreshToken}
                    headers = {"Content-Type": "application/json"}
                    token = NetworkRequest.post(
                        "http://localhost:8000/api/auth/token", headers, data=data
                    )
                    if token["code"] == 200:
                        auth.accessToken = token["body"]["access_token"]
                        auth.refreshToken = token["body"]["refresh_token"]
                        print("Reauthenticated successfully!\n")
                        return func(self, *args, **kwargs)
                    else:
                        print("Failed to authenticate!")
                        with open("log.txt", "a") as myfile:
                            myfile.write("Failed to authenticate!")
            else:
                return res

        return wrapper


class Twitter:
    def __init__(self):
        self.usedTweets = set()

    def tweetGenerator(self, n):
        value = 0
        while value < n:
            joke = get_joke()
            while joke in self.usedTweets:
                joke = get_joke()
            yield joke
            self.usedTweets.add(joke)
            value += 1

    @logger
    @Authentication.decorator
    def getRecentTweets(self, limit=1, skip=0, auth=None):
        params = {"limit": limit, "skip": skip}
        headers = {"Authorization": f"Bearer {auth.accessToken}"}
        res = NetworkRequest.get(
            "http://localhost:8000/api/tweets?", headers=headers, params=params
        )
        if res["code"] == 200:
            for tweet in res["body"]:
                print(tweet["author"]["username"], " tweeted at ", tweet["created_at"])
                print(tweet["text"])
                with open("log.txt", "a") as myfile:
                    myfile.write(
                        f'{tweet["author"]["username"]} tweeted at {tweet["created_at"]}\n'
                    )
                    myfile.write(f'{tweet["text"]}\n')

        else:
            if res["reason"]:
                print("Could not get tweets!", end=" ")
                print(res["reason"], end=".\n")
                with open("log.txt", "a") as myfile:
                    myfile.write("Could not get tweets! ")
                    myfile.write(f'{res["reason"]}.\n')

        return res

    @logger
    @Authentication.decorator
    def postTweets(self, value, auth=None):
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
            with open("log.txt", "a") as myfile:
                myfile.write(f"{value}\n")
                myfile.write("Posted 1 tweet. Sleeping for 1 minute now.\n")

        else:
            if res["reason"]:
                print("Could not post tweet!", end=" ")
                print(res["reason"], end=".\n")
                with open("log.txt", "a") as myfile:
                    myfile.write("Could not post tweet! ")
                    myfile.write(f'{res["reason"]}.\n')

        return res
