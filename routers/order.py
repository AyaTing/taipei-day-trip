from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from database import get_db_dependency
from models.user_model import get_current_user
from models.booking_model import get_booking_data_by_user_id
from models.order_model import OrderData, create_order_from_booking, process_payment, get_order_by_order_number

router = APIRouter(prefix="/api", tags=["api"])

@router.post("/orders")
async def create_order(orderData: OrderData, user: dict= Depends(get_current_user), db=Depends(get_db_dependency)):
    if not user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": f"請先登入系統"},
        )
    current_user = user["data"]["id"]
    try:
        booking = get_booking_data_by_user_id(current_user, db) 
        if not booking:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": True, "message": f"資料載入錯誤，請重新預定行程"},
        )
        order_number = create_order_from_booking(current_user, booking, orderData, db)
        if not order_number:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": True, "message": f"訂單建立失敗，請重試"},
        )
        payment_result = process_payment(orderData, booking, order_number, current_user, db)
        if payment_result["status"] == 0:
            return {"data": {"number": order_number,"payment": {"status": 0, "message": "付款成功"}}}
        else:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": True, "message": f"{payment_result['message']}"},
        )
    except Exception as err:
        print(f"伺服器錯誤：{err}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": f"發生未預期錯誤：{err}"},
        )

@router.get("/order/{orderNumber}")
async def get_order(orderNumber: str, user: dict= Depends(get_current_user), db=Depends(get_db_dependency)):
    if not user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": f"請先登入系統"},
        )
    current_user = user["data"]["id"]
    try:
        order = get_order_by_order_number(orderNumber, current_user, db)
        if order:
            return order
        else: 
            return {"data": None}
    except Exception as err:
        print(f"伺服器錯誤：{err}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": f"發生未預期錯誤：{err}"},
        )
