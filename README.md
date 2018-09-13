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
    - `Flask-HTTPAuth` - add support for HTTP simple auth used for user authentication
    - `Flask-Migrate`  - integrate Flask, Alembic (and SQLAlchemy)
    - `Flask-SQLAlchemy` - integration of SQLAlchemy ORM inside Flask
- **Database** *(PostgreSQL)*
    - `PsycoPG2-binary` - PostgreSQL driver (compiled binary)
    - `SQLAlchemy`` - Python's best ORM
    - `Alembic`` - migrations manager for SQLAlchemy
- **Security**
    - `Passlib` - easy, fast and reliable library for password hashing
        - `argon2pure` - pure Python implementation of Argon2 password hashing algorithm (must switch to C compiled version for better performance)
- **Production Performance**
    - `Tornado` - add WebSocket support and high performance (concorrent workers)
        - `gevent` - enable Tornado concurrency
- **AMQP**
    - `pika` - library for AMQP protocol
    - `requests` - Pythonic HTTP library to send requests to main Flask/Tornado server


## API Reference

### **GET** - /db/api/v0.1/users

#### CURL

```sh
curl -X GET "https://appunti-db.herokuapp.com/db/api/v0.1/users"
```

### **POST** - /db/api/v0.1/users

#### CURL

```sh
curl -X POST "https://appunti-db.herokuapp.com/db/api/v0.1/users" \
    -H "Content-Type: application/json; charset=utf-8" \
    --data-raw "$body" \
-u "test":"$password"
```

#### Header Parameters

- **Content-Type** should respect the following schema:

```
{
  "type": "string",
  "enum": [
    "application/json; charset=utf-8"
  ],
  "default": "application/json; charset=utf-8"
}
```

#### Body Parameters

- **body** should respect the following schema:

```
{
  "type": "string",
  "default": "{\"username\":\"test\",\"mail\":\"test@test.com\",\"password\":\"\"}"
}
```

#### Security

- Basic Authentication
  - **username**: test
  - **password**: $password

### **GET** - /db/api/v0.1/users/rRZCgStOp0g/auth

#### CURL

```sh
curl -X GET "https://appunti-db.herokuapp.com/db/api/v0.1/users/rRZCgStOp0g/auth" \
-u "rRZCgStOp0g":"$password"
```

#### Path Parameters

- **RequestVariable** should respect the following schema:

```
{
  "type": "string",
  "default": "rRZCgStOp0g"
}
```

#### Security

- Basic Authentication
  - **username**: rRZCgStOp0g
  - **password**: $password

### **DELETE** - /db/api/v0.1/users/rRZCgStOp0g

#### CURL

```sh
curl -X DELETE "https://appunti-db.herokuapp.com/db/api/v0.1/users/rRZCgStOp0g" \
-u "rRZCgStOp0g":"$password"
```

#### Path Parameters

- **RequestVariable** should respect the following schema:

```
{
  "type": "string",
  "default": "rRZCgStOp0g"
}
```

#### Security

- Basic Authentication
  - **username**: rRZCgStOp0g
  - **password**: $password

### **GET** - /db/api/v0.1/search

#### Description
Search all stored notes.

#### CURL

```sh
curl -X GET "https://appunti-db.herokuapp.com/db/api/v0.1/search\
?query=Fisica"
```

#### Query Parameters

- **query** should respect the following schema:

```
{
  "type": "string",
  "enum": [
    "Fisica"
  ],
  "default": "Fisica"
}
```

### **GET** - /db/api/v0.1/notes

#### CURL

```sh
curl -X GET "https://appunti-db.herokuapp.com/db/api/v0.1/notes"
```

### **POST** - /db/api/v0.1/notes

#### CURL

```sh
curl -X POST "https://appunti-db.herokuapp.com/db/api/v0.1/notes" \
    -H "Content-Type: application/json; charset=utf-8" \
    --data-raw "$body" \
-u "test":"$password"
```

#### Header Parameters

- **Content-Type** should respect the following schema:

```
{
  "type": "string",
  "enum": [
    "application/json; charset=utf-8"
  ],
  "default": "application/json; charset=utf-8"
}
```

#### Body Parameters

- **body** should respect the following schema:

```
{
  "type": "string",
  "default": "{\"name\":\"Test Note 1234\",\"owner\":\"rRZCgStOp0g\",\"teacher\":\"Sibilia\",\"subject\":\"fisica\",\"university\":\"sapienza\",\"year\":\"2016\",\"tags\":[\"exercises\"],\"language\":\"ita\"}"
}
```

#### Security

- Basic Authentication
  - **username**: test
  - **password**: $password

### **DELETE** - /db/api/v0.1/notes/82f8AjF3WzE

#### CURL

```sh
curl -X DELETE "https://appunti-db.herokuapp.com/db/api/v0.1/notes/82f8AjF3WzE" \
-u "test":"$password"
```

#### Path Parameters

- **ResponseBodyPath** should respect the following schema:

```
{
  "type": "string",
  "default": "82f8AjF3WzE"
}
```

#### Security

- Basic Authentication
  - **username**: test
  - **password**: $password

### **GET** - /db/api/v0.1/amqp/SIo7LfcujeQ/1/0002

#### CURL

```sh
curl -X GET "https://appunti-db.herokuapp.com/db/api/v0.1/amqp/SIo7LfcujeQ/1/0002"
```

### **POST** - /db/api/v0.1/files/82f8AjF3WzE

#### CURL

```sh
curl -X POST "https://appunti-db.herokuapp.com/db/api/v0.1/files/82f8AjF3WzE" \
    -H "Content-Type: multipart/form-data; charset=utf-8; boundary=__X_PAW_BOUNDARY__" \
    --data-raw "enctype"="multipart/form-data" \
    --data-raw "file1"="$file1" \
-u "test":"$password"
```

#### Path Parameters

- **RequestVariable** should respect the following schema:

```
{
  "type": "string",
  "default": "82f8AjF3WzE"
}
```

#### Header Parameters

- **Content-Type** should respect the following schema:

```
{
  "type": "string",
  "enum": [
    "multipart/form-data; charset=utf-8; boundary=__X_PAW_BOUNDARY__"
  ],
  "default": "multipart/form-data; charset=utf-8; boundary=__X_PAW_BOUNDARY__"
}
```

#### Body Parameters

- **enctype** should respect the following schema:

```
{
  "type": "string",
  "enum": [
    "multipart/form-data"
  ],
  "default": "multipart/form-data"
}
```
- **file1** should respect the following schema:

```
{
  "type": "string",
  "enum": [
    ""
  ]
}
```

#### Security

- Basic Authentication
  - **username**: test
  - **password**: $password

### **GET** - /db/api/v0.1/files/82f8AjF3WzE/1

#### CURL

```sh
curl -X GET "https://appunti-db.herokuapp.com/db/api/v0.1/files/82f8AjF3WzE/1"
```

#### Path Parameters

- **RequestVariable** should respect the following schema:

```
{
  "type": "string",
  "default": "82f8AjF3WzE"
}
```
- **RequestVariable_2** should respect the following schema:

```
{
  "type": "string",
  "default": "1"
}
```

### **PUT** - /db/api/v0.1/files/82f8AjF3WzE

#### CURL

```sh
curl -X PUT "https://appunti-db.herokuapp.com/db/api/v0.1/files/82f8AjF3WzE" \
    -H "Content-Type: multipart/form-data; charset=utf-8; boundary=__X_PAW_BOUNDARY__" \
    --data-raw "enctype"="multipart/form-data" \
    --data-raw "file_to_append"="$file_to_append" \
-u "test":"$password"
```

#### Path Parameters

- **RequestVariable** should respect the following schema:

```
{
  "type": "string",
  "default": "82f8AjF3WzE"
}
```

#### Header Parameters

- **Content-Type** should respect the following schema:

```
{
  "type": "string",
  "enum": [
    "multipart/form-data; charset=utf-8; boundary=__X_PAW_BOUNDARY__"
  ],
  "default": "multipart/form-data; charset=utf-8; boundary=__X_PAW_BOUNDARY__"
}
```

#### Body Parameters

- **enctype** should respect the following schema:

```
{
  "type": "string",
  "enum": [
    "multipart/form-data"
  ],
  "default": "multipart/form-data"
}
```
- **file_to_append** should respect the following schema:

```
{
  "type": "string",
  "enum": [
    ""
  ]
}
```

#### Security

- Basic Authentication
  - **username**: test
  - **password**: $password


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
```
-e B2_APPLICATION_KEY='XXXXXXXXX...XXXXXXXX'
-e B2_ACCOUNT_ID='XXXX...XXXX'
-e AMQP_BROKER_URL='amqp://USERNAME:PASSWORD@URL'
-e APPLICATION_MODE='PRODUCTION or TESTING or DEVELOPMENT'
-e DATABASE_URL='postgres://USERNAME:PASSWORD@URL'
-e ADDRESS='0.0.0.0'
-e PORT='INT_PORT'
```
