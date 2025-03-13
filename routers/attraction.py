from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from database import get_db_dependency
import mysql.connector

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/attractions")
async def get_attractions_list(page: int, keyword: str=None, db=Depends(get_db_dependency)):
    limit = 12
    offset = page * limit
    if page < 0:
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": True, "message": f"分頁號碼不在範圍內"}
            )
    try:
        cursor = db.cursor(dictionary=True)
        if keyword == None:
            select_query = "SELECT `id`, `name`, `category`, `description`, `address`, `transport`, `mrt`, `lat`, `lng` FROM `attractions` LIMIT %s OFFSET %s"
            cursor.execute(select_query, (limit + 1, offset))
            attractions = cursor.fetchall()
            if not attractions:
                return {"nextPage": None, "data": []}
        else:
            select_query = "SELECT `id`, `name`, `category`, `description`, `address`, `transport`, `mrt`, `lat`, `lng` FROM `attractions` WHERE `mrt` = %s OR `name` LIKE %s LIMIT %s OFFSET %s"
            cursor.execute(select_query, (keyword, f"%{keyword}%", limit + 1, offset))
            attractions = cursor.fetchall()
            if not attractions:
                return {"nextPage": None, "data": []}
        attraction_ids = tuple(attr["id"] for attr in attractions)
        if attraction_ids:
            placeholders = ",".join(["%s"] * len(attraction_ids))
            select_query = f"SELECT `attraction_id`, `image_url` FROM `attraction_images` WHERE `attraction_id` IN ({placeholders})"
            cursor.execute(select_query, attraction_ids)
            image_urls = cursor.fetchall()
            image_dict = {}
            for image_url in image_urls:
                image_dict.setdefault(image_url["attraction_id"],[]).append(image_url["image_url"])
            for attr in attractions:
                attr["images"] = image_dict.get(attr["id"], [])
        data = attractions[:limit]
        next_page = page + 1 if len(attractions) > limit else None
        return {"nextPage": next_page, "data": data}
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
@router.get("/attraction/{attractionId}")
async def get_attraction(attractionId: int, db=Depends(get_db_dependency)):
    try:
        cursor = db.cursor(dictionary=True)
        select_query = "SELECT `id`, `name`, `category`, `description`, `address`, `transport`, `mrt`, `lat`, `lng` FROM `attractions` WHERE `id` = %s"
        cursor.execute(select_query, (attractionId,))
        attraction = cursor.fetchone()
        if not attraction:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": True, "message": f"景點編號不正確"}
            )
        select_query = "SELECT `image_url` FROM `attraction_images` WHERE `attraction_id` = %s"
        cursor.execute(select_query, (attractionId,))
        image_urls = [url["image_url"] for url in cursor.fetchall()]
        attraction["images"] = image_urls
        return {"data": attraction}
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
