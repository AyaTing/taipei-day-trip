from fastapi import Depends, Header
from database import get_db_dependency
from pydantic import BaseModel, Field, EmailStr
import mysql.connector
import jwt
from dotenv import load_dotenv
import bcrypt
import os

load_dotenv()
JWT_KEY = os.getenv("JWT_KEY")

class SignUpData(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)

class SignInData(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


def create_user(name, email, password, db):
    cursor = db.cursor()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    insert_query = "INSERT INTO `users`(`name`, `email`, `password`) VALUES(%s, %s, %s)"
    try:
        cursor.execute(insert_query, (name, email, hashed_password))
        db.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        db.rollback()
        if err.errno == 1062:
            raise ValueError("此E-mail已註冊。")
        raise Exception(f"伺服器發生錯誤: {err}")
    finally:
        cursor.close()


def get_user_by_email(email, db):
    try:
        cursor = db.cursor(dictionary=True)
        select_query = "SELECT * FROM `users` WHERE `email` = %s"
        cursor.execute(select_query, (email,))
        return cursor.fetchone()
    finally:
        cursor.close()

def get_user_by_id(user_id, db):
    try:
        cursor = db.cursor(dictionary=True)
        select_query = "SELECT `id`, `name`, `email` FROM `users` WHERE `id` = %s"
        cursor.execute(select_query, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()


def verify_user_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")) 


async def get_current_user(authorization: str = Header(None), db=Depends(get_db_dependency)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"data": None}
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
        user = get_user_by_id(payload["sub"], db)
        if not user:
            return {"data": None}
        return {"data": {"id": user["id"], "name": user["name"], "email": user["email"]}}
    except jwt.PyJWTError as err:
        print("JWT Error:", str(err))
        return {"data": None}
