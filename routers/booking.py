from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from database import get_db_dependency
from models.user_model import get_current_user
from models.booking_model import BookingData, calculate_price, save_booking, get_booking_data_by_user_id, delete_booking_by_user_id
from mysql.connector import Error 


router = APIRouter(prefix="/api", tags=["api"])


@router.post("/booking")
async def create_booking(booking_data: BookingData, user: dict= Depends(get_current_user), db=Depends(get_db_dependency)):
    if not user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": f"請先登入系統"},
        )
    current_user = user["data"]["id"]
    booking_data.price = calculate_price(booking_data.time)
    try: 
        booking_status = "pending"
        save_booking(current_user, booking_data, booking_status, db)
        return {"ok": True}
    except Error as err:
        if err.errno == 1452:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": True, "message": f"此景點不存在：{err}"},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": f"資料庫發生錯誤：{err}"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": f"系統發生錯誤：{e}"},
        )

@router.delete("/booking")
async def delete_booking(user: dict= Depends(get_current_user), db=Depends(get_db_dependency)):
    if not user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": f"請先登入系統"},
        )
    current_user = user["data"]["id"]
    try: 
        delete_booking_by_user_id(current_user, db)
        return {"ok": True}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": f"系統發生錯誤：{e}"},
        )



@router.get("/booking")
async def get_booking(user: dict= Depends(get_current_user), db=Depends(get_db_dependency)):
    if not user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": f"請先登入系統"},
        )
    current_user = user["data"]["id"]
    try:
        booking = get_booking_data_by_user_id(current_user, db) 
        if not booking:
            return {"data": None}
        return {"data": booking}
    except Exception as err:
        print(f"伺服器錯誤：{err}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": f"發生未預期錯誤：{err}"},
        )
    
