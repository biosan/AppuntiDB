# Project Note Database Back-end

## Introduction

This repository contains Appunti-DB, the database back-end for Project Note, a platform for note sharing.
Appunti-DB is written in Python using Flask framework running on Tornado WSGI server, everything is packed in a Docker container that allow fast, reproducible and dependency-less deployment.


## Architecture

```
+-------------------------------------+
|               My Code               |
|--------+                +-----------|
|  Pika  |                | WebSocket |
+-------------------------------------+
     |             |              |
     |             V              |
     |     +---------------+      |
     |     | Flask-Restful |      |
     |     +---------------+      |
     |             |              |
     |             V              |
     |       +-----------+        |
     |       |   Flask   |        |
     |       +-----------+        |
     |             |              |
     |AMQP         |HTTP          |WebSocket
     |             |              |
     V             V              V
 +------+   +-------------------------+
 | Pika |   |      Tornado WSGI       |
 +------+   +-------------------------+
+======================================+
|            Supervisord               |
+======================================+
+======================================+
|              Docker                  |
+======================================+
```

### Libraries and dependencies

- **Flask**
    - `Flask-Restful`- to reduce Flask boilerplate for API-only services)
    - `Flask-Script`- allow CLI-like management of Flask
    - Flask-HTTPAuth - add support for HTTP simple auth used for user authentication 
    - Flask-Migrate  - integrate Flask, Alembic (and SQLAlchemy) 


flask
flask_restful
psycopg2-binary
Flask-Migrate
Flask-Script
flask_sqlalchemy
flask-socketio
gevent
pika
requests
tornado
flask_httpauth
argon2pure
passlib


## Code Example

Show what the library does as concisely as possible, developers should be able to figure out how your project solves their problem by looking at the code example. Make sure the API you are showing off is obvious, and that your code is short and concise.

## Motivation

A short description of the motivation behind the creation and maintenance of the project. This should explain why the project exists.

## Installation

Provide code examples and explanations of how to get the project.

## API Reference

Depending on the size of the project, if it is small and simple enough the reference docs can be added to the README. For medium size to larger projects it is important to at least provide a link to where the API reference docs live.

Tests

Describe and show how to run the tests with code examples.

## Contributors

Let people know how they can dive into the project, include important links to things like issue trackers, irc, twitter accounts if applicable.

## License

A short snippet describing the license (MIT, Apache, etc.)




## Building container

To build the container run this inside this repo
```
docker build -t db_api .
```

To run it
```
docker run db_api -p INT_PORT:EXT_PORT
```

### Environment variables
-e B2_APPLICATION_KEY='XXXXXXXXX...XXXXXXXX'
-e B2_ACCOUNT_ID='XXXX...XXXX'
-e AMQP_BROKER_URL='amqp://USERNAME:PASSWORD@URL'
-e APPLICATION_MODE='PRODUCTION or TESTING or DEVELOPMENT'
-e DATABASE_URL='postgres://USERNAME:PASSWORD@URL'
-e ADDRESS='0.0.0.0'
-e PORT='INT_PORT'


## API Usage

### HTTP Endpoints

- Users
    1. Add user
    2. Delete user
- Notes
    1. Add note
        `POST /user
        asdfa
        asdfas
    2. Delete note
    3. Upload note's file
    4. Delete note's file
    5. Search notes

/users/<uid>
/users

/notes
/notes/<nid>

/search

/files/<nid>
/files/<nid>/page

