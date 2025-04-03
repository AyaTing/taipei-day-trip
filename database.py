import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
import os
from contextlib import contextmanager
import bcrypt

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE"),
    "pool_name": "tourism_pool",
    "pool_size": 5,
    "pool_reset_session": True,
}

try:
    connection_pool = pooling.MySQLConnectionPool(**DB_CONFIG)
except mysql.connector.Error as err:
    print(f"無法建立連線池：{err}")
    raise

@contextmanager
def get_db_connection():
    try:
        db = connection_pool.get_connection()
        try:
            yield db
        finally:
            db.close()
    except mysql.connector.Error as err:
        print(f"資料庫連線失敗：{err}")
        raise

def get_db():
    return get_db_connection()

def get_db_dependency():
    with get_db_connection() as db:
        yield db


def save_attraction_data(attraction_data, image_urls):
    with get_db() as db:
        cursor = db.cursor()
        insert_query = "INSERT INTO `attractions`(`name`, `category`, `description`, `address`, `transport`, `mrt`, `lat`, `lng`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            attraction_data["name"],
            attraction_data["category"],
            attraction_data["description"],
            attraction_data["address"],
            attraction_data["transport"],
            attraction_data["mrt"],
            attraction_data["lat"],
            attraction_data["lng"],
        )
        cursor.execute(insert_query,values)
        attraction_id = cursor.lastrowid
        for url in image_urls:
            insert_query = "INSERT INTO `attraction_images`(`attraction_id`,`image_url`) VALUES (%s, %s)"
            cursor.execute(insert_query, (attraction_id,url))
        db.commit()
        return attraction_id
    
def clear_attraction_data():
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM `attraction_images`")
        cursor.execute("DELETE FROM `attractions`")
        cursor.execute("ALTER TABLE `attractions` AUTO_INCREMENT = 1")
        db.commit()


def get_mrts_data(db):
    cursor = db.cursor()
    select_query = "SELECT `mrt`, COUNT(*) AS `attraction_count` FROM `attractions` WHERE `mrt` IS NOT NULL GROUP BY `mrt` ORDER BY `attraction_count` DESC"
    cursor.execute(select_query)
    return cursor.fetchall()


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


def get_user_by_email(email, db):
    cursor = db.cursor(dictionary=True)
    select_query = "SELECT * FROM `users` WHERE `email` = %s"
    cursor.execute(select_query, (email,))
    return cursor.fetchone()

def get_user_by_id(user_id, db):
    cursor = db.cursor(dictionary=True)
    select_query = "SELECT `id`, `name`, `email` FROM `users` WHERE `id` = %s"
    cursor.execute(select_query, (user_id,))
    return cursor.fetchone()


def verify_user_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")) 