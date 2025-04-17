from pydantic import BaseModel, EmailStr
import datetime
from datetime import timezone
import os
from dotenv import load_dotenv
import urllib.request
import urllib.error
import json
from models.attraction_model import get_attraction_by_id

os.environ["no_proxy"] = "*"
load_dotenv()

TAPPAY_MERCHANT_ID = os.getenv("TAPPAY_MERCHANT_ID")
TAPPAY_PARTNER_KEY = os.getenv("TAPPAY_PARTNER_KEY")
TAPPAY_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"


class OrderData(BaseModel):
    prime: str
    name: str
    email: EmailStr
    phone: str


def generate_order_number(attraction_id, user_id):
    order_number = datetime.datetime.now(tz=timezone.utc).strftime(f"%Y%m%d%H%M%S-{attraction_id}-{user_id}")
    return order_number

def create_order_from_booking(user_id, booking, order_data, db):
    order_number = generate_order_number(booking["attraction"]["id"], user_id)
    try:
        cursor = db.cursor()
        insert_query = "INSERT INTO `orders` (`order_number`, `user_id`, `attraction_id`, `date`, `time`, `price`, `contact_name`, `contact_email`, `contact_phone`, `status`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'UNPAID')"
        values = (order_number, user_id, booking["attraction"]["id"], booking["date"], booking["time"], booking["price"], order_data.name, order_data.email, order_data.phone)
        cursor.execute(insert_query, values)
        db.commit()
        return order_number
    except Exception as err:
        db.rollback()
        raise err
    finally: 
        cursor.close()


def process_payment(orderData, booking, order_number, user_id, db):
    try:
        payload = {
            "prime": orderData.prime,
            "partner_key": TAPPAY_PARTNER_KEY,
            "merchant_id": TAPPAY_MERCHANT_ID,
            "details": f"台北一日遊：{booking['date']} {booking['attraction']['name']} - 訂單 {order_number}",
            "amount": booking["price"],
            "cardholder": {
                "phone_number": orderData.phone,
                "name": orderData.name,
                "email": orderData.email,
            },
            "remember": False
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        headers = {
                "Content-Type": "application/json",
                "x-api-key": TAPPAY_PARTNER_KEY
            }
        req = urllib.request.Request(TAPPAY_URL, data=payload_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise urllib.error.URLError(f"系統回應錯誤: {response.status}")
            result = json.loads(response.read().decode('utf-8'))
            print(result)
            payment_status = result.get("status")
            print(payment_status)
            payment_message = result.get("msg")
            print(payment_message)
        cursor = db.cursor()
        if payment_status == 0:
            update_order_query = "UPDATE `orders` SET `status` = 'PAID' WHERE `order_number` = %s"
            cursor.execute(update_order_query, (order_number,))
            update_booking_query = "UPDATE `bookings` SET `status` = 'confirmed' WHERE `user_id` = %s AND `status` = 'pending'"
            cursor.execute(update_booking_query, (user_id,))
            db.commit()
            payment_message = "付款成功"
        else:
            payment_message = "付款失敗"
        return {
            "status": payment_status,
            "message": payment_message
        }
    except urllib.error as err:
        db.rollback()
        return {
            "status": payment_status,
            "message": f"{payment_message}：{str(err)}"
        }
    except Exception as e:
        db.rollback()
        return {
            "status": 500,
            "message": f"系統錯誤: {str(e)}"
        }
    finally:
        cursor.close()

def get_order_by_order_number(order_number, user_id, db):
    try:
        cursor = db.cursor(dictionary=True)
        select_query = "SELECT * FROM `orders` WHERE `order_number` = %s AND `user_id` = %s"
        cursor.execute(select_query, (order_number, user_id))
        order = cursor.fetchone()
        if not order:
            return None
        attraction = get_attraction_by_id(order["attraction_id"], db)
        attraction["images"] = attraction.pop("images").split(",")
        attraction_image = attraction["images"][0]
        formatted_order = {
            "data": {
            "number": order_number,
            "price": order["price"],
            "trip": {
                "attraction": {
                "id": order["attraction_id"],
                "name": attraction["name"],
                "address": attraction["address"] ,
                "image": attraction_image
                },
                "date": order["date"],
                "time": order["time"]
            },
            "contact": {
                "name": order["contact_name"],
                "email": order["contact_email"],
                "phone": order["contact_phone"]
            },
            "status": order["status"]
            }
        }
        return formatted_order
    except Exception as err:
        db.rollback()
        raise err
    finally: 
        cursor.close()


