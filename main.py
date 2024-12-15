from util import Authentication, Twitter
from time import sleep


def main():
    auth = Authentication()
    twitter = Twitter()
    while auth.accessToken is None:
        choice = input("Enter 1 to register or 2 to login: ")
        if choice == "1":
            auth.register()
        elif choice == "2":
            auth.login()

    if auth.accessToken:
        print("Checking recent tweets...\n")
        for i in range(6):
            twitter.getRecentTweets(1, i, auth=auth)
            sleep(2)
        print("Posting tweets...\n")
        for value in twitter.tweetGenerator(10):
            twitter.postTweets(value, auth=auth)
            sleep(30)

    print("Exiting...")


if __name__ == "__main__":
    main()
