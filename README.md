## Classes and functions

### `main` function

The main function instatiates an `Authentication` object, which provides login
and register functionality and acts as the token store. When the user is
successfully logged in, it calls the `getRecentTweets` function, followed the
`postTweets` function. Finally, it writes these logs to a file before exiting.

### `Twitter` class

Methods: `getRecentTweets`, which makes a NetworkRequest to the server to get
the 5 most recent tweets, and `postTweets`, which calls the `generator` method
to genrate and post 10 tweets every minute using the `pyjokes` package. It also
keeps a set to store used jokes, so the same joke is not repeated.

### `Authenticate` class

Variables: `access_token`, `refresh_token`, `currentUser`

The `Authenticate` has two methods, `register` and `login`, that perform their
namesake tasks.

### `reauthenticate` decorator

The `reaunthenticate` decorator wraps each `Twitter` method. If access_token is
expired (response is 401), it will use the refresh token to get a new access
token, and then rerun the function. If retry returns 401, exit with an
appropriate message.

### `logger` decorator

This will log the execution time.

## Challenges

From the `urllib.request` documentation,

"An appropriate Content-Type header should be included if the data argument is
present. If this header has not been provided and data is not None,
Content-Type: application/x-www-form-urlencoded will be added as a default."
[1](https://docs.python.org/3/library/urllib.request.html#urllib.request.Request)

Without this header, I was getting the `422 Unprocessable Entity` error, which I
spent a lot of time debugging.

Implementing the token refreshing mechanism was also a challenge. Raising an
HTTP error, handling it gracefully, showing a meaningful message to the user,
and then letting the decorator perform the token refresh took some time. In the
end, I realized raising an HTTP error was making my code verbose and it did not
serve a real purpose in the program, so I instead opted to make the decorator
simply inform the user that it is performing reauthentication before doing it.
Note that the decorator does not retry if the refresh token also fails to
reauthenticate.
