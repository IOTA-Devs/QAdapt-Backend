# QAdapt-Backend

## Installation
pip install -r requirements.txt
uvicorn main:app --reload

## dotenv
Create a .env file in the root directory and add the following variables:
```
ACCESS_TOKEN_SECRET_KEY
PERSONAL_TOKEN_SECRET_KEY
DB_PASSWORD <- password for your postgres database
```

## Database
Refer to db/dbQAdaptDB.sql for the database schema