from util import Authentication, Twitter

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
        twitter.getRecentTweets(auth)
        twitter.postTweets(auth)
    

if __name__ == '__main__':
    main()
