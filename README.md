## Run with watchdog

```
pip install watchdog
```

Then run

```
watchmedo auto-restart --patterns="*.py" --recursive -- python main.py
```

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

This will log the execution time of the function it wraps.

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

Deleting a tweet logs an indescript error message on the server:

<details>
<summary>Stack trace</summary>

```
RuntimeError: Response content longer than Content-Length
INFO:     127.0.0.1:50668 - "DELETE /api/tweets/87 HTTP/1.1" 204 No Content
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/uvicorn/protocols/http/httptools_impl.py", line 372, in run_asgi
    result = await app(self.scope, self.receive, self.send)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/uvicorn/middleware/proxy_headers.py", line 75, in __call__
    return await self.app(scope, receive, send)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/fastapi/applications.py", line 269, in __call__
    await super().__call__(scope, receive, send)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/applications.py", line 124, in __call__
    await self.middleware_stack(scope, receive, send)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/middleware/errors.py", line 184, in __call__
    raise exc
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/middleware/errors.py", line 162, in __call__
    await self.app(scope, receive, _send)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/exceptions.py", line 93, in __call__
    raise exc
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/exceptions.py", line 82, in __call__
    await self.app(scope, receive, sender)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in __call__
    raise e
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/routing.py", line 670, in __call__
    await route.handle(scope, receive, send)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/routing.py", line 266, in handle
    await self.app(scope, receive, send)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/routing.py", line 68, in app
    await response(scope, receive, send)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/responses.py", line 162, in __call__
    await send({"type": "http.response.body", "body": self.body})
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/exceptions.py", line 79, in sender
    await send(message)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/starlette/middleware/errors.py", line 159, in _send
    await send(message)
  File "~/projects/Intern-Test-Server/.venv/lib/python3.8/site-packages/uvicorn/protocols/http/httptools_impl.py", line 501, in send
    raise RuntimeError("Response content longer than Content-Length")
RuntimeError: Response content longer than Content-Length
```
</details>

Although the tweet is still deleted successfully, this issue remains to be debugged.