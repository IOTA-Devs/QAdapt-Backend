# QAdapt-Backend

## Installation
pip install -r requirements.txt

## dotenv
Create a .env file in the root directory and add the following variables:
```
ACCESS_TOKEN_SECRET_KEY <- Cryptographically secure random string for generating access tokens 
PERSONAL_TOKEN_SECRET_KEY <- Cryptographically secure random string for generating refresh tokens 

DB_HOST <- host url for the database
DB_USER <- database access user
DB_NAME <- database name
DB_PASSWORD <- password for your postgres database
```

## Database
Refer to db/dbQAdaptDB.sql for the database schema

## Run
```
fastapi dev main.py
```
