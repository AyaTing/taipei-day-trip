from fastapi import APIRouter, Depends, status, Header
from fastapi.responses import JSONResponse
from database import get_db_dependency
from models.user_model import create_user, get_user_by_email, verify_user_password, get_user_by_id, SignUpData,SignInData
import os
import jwt
import datetime
from datetime import timezone
from dotenv import load_dotenv

load_dotenv()
JWT_KEY = os.getenv("JWT_KEY")

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/user")
async def signup(user: SignUpData, db=Depends(get_db_dependency)):
    try:
        create_user(user.name, user.email, user.password, db)
        return {"ok": True}
    except ValueError as err:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": True, "message": str(err)})
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": True, "message": str(err)})


@router.get("/user/auth")
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


@router.put("/user/auth")
async def signin(user: SignInData, db=Depends(get_db_dependency)):
    try:
        db_user = get_user_by_email(user.email, db)
        if not db_user or not verify_user_password(user.password, db_user["password"]):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": True, "message": "登入失敗，帳號或密碼錯誤"})
        payload = {"sub": str(db_user["id"]), "iat": datetime.datetime.now(tz=timezone.utc), "exp": datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(minutes=7 * 24 * 60)}
        token = jwt.encode(payload , JWT_KEY, algorithm="HS256")
        return {"token": token}
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": True, "message": f"伺服器發生錯誤: {err}"})