# Pastebin API with Fastapi and Tortoise ORM

This sample application is inspired by the Django Rest Framework
[tutorial](https://www.django-rest-framework.org/tutorial/1-serialization/). I made it to learn usage of
[FastAPI](https://fastapi.tiangolo.com/) with [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/).

To test it, you must install the project with poetry.

```shell
$ poetry install
```

You also need to initialize the database with [aerich](https://tortoise-orm.readthedocs.io/en/latest/migration.html).

```shell
$ aerich init-db
$ aerich upgrade
```

If you want pygments languages and styles to play with, there is a simple CLI to populate the related tables.

```shell
$ pastebin add-lang-to-db
$ pastebin add-styles-to-db
```

And if you want to create administrator users to play with authentication, there is also a CLI command for that purpose.

```shell
$ pastebin add-admin-user
# fill the information requested
```

Some thoughts about this project:

- FastAPI has a steep learning curve (the doc is fill of information) but once mastered, you code really fast. It's a
  real pleasure that I haven't experienced since Django :)

- Tortoise ORM was what I have wanted since the awareness of async when dealing with databases. Once again, I find the
  joy of using an ORM since Django and for good reason, it's almost a copy of the latter with just the *async* keyword
  to place before the method names.

- The default test client provided by Starlette is not sufficient for async testing. I have to use
  [httpx](https://www.python-httpx.org/) for that purpose, but I was not aware of this
  [issue](https://github.com/encode/starlette/issues/652#issuecomment-537233918) which makes it impossible to run
  startup and close events (callbacks) like initializing a database. This was such a pain! I should probably have use
  [async-asig-testclient](https://pypi.org/project/async-asgi-testclient/) from the beginning. This is a lesson for the
  future.