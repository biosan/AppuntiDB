# Appunti Database Backend


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
    2. Delete note
    3. Upload note's file
    4. Delete note's file
    5. Search notes
