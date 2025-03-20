import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
import os
from contextlib import contextmanager

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