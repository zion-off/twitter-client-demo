import sys
from util import Authentication

def main():
    auth = Authentication()
    while auth.accessToken is None:
        choice = input("Enter 1 to register or 2 to login: ")
        if choice == "1":
            auth.register()
        elif choice == "2":
            auth.login()
    

if __name__ == '__main__':
    main()
