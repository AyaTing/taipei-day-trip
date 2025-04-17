from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from models.user_model import get_current_user
import os 

load_dotenv()
router = APIRouter(prefix="/api", tags=["api"])

@router.get("/payment/config")
async def get_payment_config(user: dict = Depends(get_current_user)):
    if not user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": "請先登入系統"},
        )
    return {
        "appId": int(os.getenv("TAPPAY_APP_ID")),
        "appKey": os.getenv("TAPPAY_APP_KEY"),
    }