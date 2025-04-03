from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from database import get_db_dependency, get_mrts_data
import mysql.connector

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/mrts")
async def get_mrt(db=Depends(get_db_dependency)):
    try:
        mrts = get_mrts_data(db)
        mrt_list = [mrt[0] for mrt in mrts]
        return {"data": mrt_list}
    except mysql.connector.Error as err:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": f"資料庫連線失敗：{err}"},
        )
    except Exception as err:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": f"發生未預期錯誤：{err}"},
        )
