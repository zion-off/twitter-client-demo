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
        else:
            continue

    if auth.accessToken:
        print(auth.accessToken)
        menuItem = "-1"
        while menuItem != "5":
            print("To check recent tweets, enter 1.")
            print("To post 10 tweets, enter 2.")
            print("To update a tweet (with an ID), enter 3.")
            print("To delete a tweet (with an ID), enter 4.")
            print("To exit, enter anything else.")
            menuItem = input("> ")
            print()
            if menuItem == "1":
                print("Checking recent tweets...\n")
                with open("log.txt", "a") as myfile:
                    myfile.write("Checking recent tweets...\n")
                for i in range(6):
                    res = twitter.getRecentTweets(1, i, auth=auth)
                    if res is None:
                        continue
            elif menuItem == "2":
                print("Posting tweets...\n")
                with open("log.txt", "a") as myfile:
                    myfile.write("Posting tweets...\n")
                for value in twitter.tweetGenerator(10):
                    twitter.postTweets(value, auth=auth)
                    sleep(30)
            elif menuItem == "3":
                twitter.updateTweet(auth=auth)
            elif menuItem == "4":
                twitter.deleteTweet(auth=auth)
            else:
                print("Exiting...")
                with open("log.txt", "a") as myfile:
                    myfile.write("Exiting...")
                break


if __name__ == "__main__":
    main()
