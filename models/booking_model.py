from pydantic import BaseModel, field_validator
from datetime import date
from typing import Literal, Optional


class BookingData(BaseModel): 
    attraction_id: int
    date: date
    time: Literal["morning", "afternoon"]
    price: Optional[int] = None

    @field_validator("date")
    @classmethod
    def validate_future_date(cls, value):
        today = date.today()
        if value <= today:
            raise ValueError("日期錯誤，請選擇未來的日期")
        return value

def calculate_price(time):
    tour_price = {"morning": 2000, "afternoon": 2500}
    return tour_price[time]


def save_booking(user_id, booking_data, booking_status, db):
    cursor = db.cursor()
    try:
        delete_booking_by_user_id(user_id, db)
        insert_query = "INSERT INTO `bookings`(`user_id`, `attraction_id`, `date`, `time`, `price`, `status`) VALUES(%s, %s, %s, %s, %s, %s)"
        values = (
            user_id, booking_data.attraction_id, booking_data.date, booking_data.time, booking_data.price, booking_status
        )
        cursor.execute(insert_query, values)
        booking_id = cursor.lastrowid
        db.commit()
        return booking_id 
    except Exception as err:
        db.rollback()
        raise err
    finally: 
        cursor.close()


def delete_booking_by_user_id(user_id, db):
    try:
        cursor = db.cursor()
        delete_query = "DELETE FROM `bookings` WHERE `user_id` = %s AND `status` = 'pending'"
        cursor.execute(delete_query, (user_id,))
        db.commit()
    finally: 
        cursor.close()


def get_booking_data_by_user_id(user_id, db):
    try: 
        cursor = db.cursor(dictionary=True)
        select_query = "SELECT `b`.`id`, `b`.`attraction_id`, `b`.`date`, `b`.`time`, `b`.`price`, `a`.`name`, `a`.`address`, `ai`.`image_url` FROM `bookings` `b` JOIN `attractions` `a` ON `b`.`attraction_id` = `a`.`id` LEFT JOIN `attraction_images` `ai` ON `a`.`id` = `ai`.`attraction_id` WHERE `b`.`user_id` = %s AND `b`.`status` = 'pending' LIMIT 1"
        cursor.execute(select_query, (user_id,))
        booking = cursor.fetchone()
        if not booking:
            return None
        formatted_booking ={
        "attraction": {
          "id": booking["attraction_id"],
          "name": booking["name"],
          "address": booking["address"],
          "image": booking["image_url"]
        },
        "date": booking["date"],
        "time": booking["time"],
        "price": booking["price"]
        }
        return formatted_booking
    finally: 
        cursor.close()