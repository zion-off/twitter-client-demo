import json
import time
from pyjokes import get_joke
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def logger(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Time taken: {end - start}\n")
        with open("log.txt", "a") as myfile:
            myfile.write(f"Time taken: {end - start}\n")
        return result
    return wrapper



class NetworkRequest:
    @staticmethod
    def get(url, headers={}, params=None):
        if params:
            query_string = urlencode(params)
            url = url + "?" + query_string
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
    def put(url, headers={}, data={}):
        req = Request(url=url, method="PUT", data=json.dumps(data).encode("utf-8"))
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
    def delete(url, headers={}):
        req = Request(url=url, method="DELETE")
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
        headers = {"Content-Type": "application/json"}
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
        headers = {"Content-Type": "application/json"}
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
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            # if this is not a 401 error, return early
            if res["code"] != 401:
                return res
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
                else:
                    print("Failed to authenticate!")
                    with open("log.txt", "a") as myfile:
                        myfile.write("Failed to authenticate!")
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
            "http://localhost:8000/api/tweets", headers=headers, params=params
        )
        if res["code"] == 200:
            if len(res["body"]) == 0:
                print("No more tweets to show.")
                with open("log.txt", "a") as myfile:
                    myfile.write("No more tweets to show.\n")
                return res
            for tweet in res["body"]:
                print(tweet["author"]["username"], " tweeted at ", tweet["created_at"])
                print(tweet["text"])
                with open("log.txt", "a") as myfile:
                    myfile.write(
                        f'{tweet["author"]["username"]} tweeted at {tweet["created_at"]}\n'
                    )
                    myfile.write(f'{tweet["text"]}\n')
            return res

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

    @logger
    @Authentication.decorator
    def updateTweet(self, auth=None):
        tweetID = input("Enter Tweet ID: ")
        updatedTweet = input("Enter new content: ")
        data = {"text": updatedTweet}
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {auth.accessToken}"
        res = NetworkRequest.put(
            f"http://localhost:8000/api/tweets/{tweetID}",
            headers=headers,
            data=data,
        )
        if res["code"] == 200:
            print(f"Updated Tweet #{tweetID} with text '{updatedTweet}'")
            with open("log.txt", "a") as myfile:
                myfile.write(f"Updated Tweet #{tweetID} with text '{updatedTweet}'\n")

        else:
            if res["reason"]:
                print("Could not update tweet!", end=" ")
                print(res["reason"], end=".\n")
                with open("log.txt", "a") as myfile:
                    myfile.write("Could not update tweet! ")
                    myfile.write(f'{res["reason"]}.\n')

        return res

    @logger
    @Authentication.decorator
    def deleteTweet(self, auth=None):
        tweetID = input("Enter Tweet ID: ")
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {auth.accessToken}"
        res = NetworkRequest.delete(
            f"http://localhost:8000/api/tweets/{tweetID}",
            headers=headers,
        )
        if res["code"] == 204:
            print(f"Deleted Tweet #{tweetID}.")
            with open("log.txt", "a") as myfile:
                myfile.write(f"Deleted Tweet #{tweetID}\n")

        else:
            if res["reason"]:
                print("Could not delete tweet!", end=" ")
                print(res["reason"], end=".\n")
                with open("log.txt", "a") as myfile:
                    myfile.write("Could not delete tweet! ")
                    myfile.write(f'{res["reason"]}.\n')

        return res
