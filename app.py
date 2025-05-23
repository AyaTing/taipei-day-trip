from fastapi import *
from fastapi.responses import FileResponse
from routers import attraction, mrts, user, booking, order, payconfig
from fastapi.staticfiles import StaticFiles

app=FastAPI()
app.include_router(mrts.router)
app.include_router(attraction.router)
app.include_router(user.router)
app.include_router(booking.router)
app.include_router(order.router)
app.include_router(payconfig.router)

app.mount("/static", StaticFiles(directory="static"),name="static")

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


if __name__ ==  "__main__":
    import uvicorn
    uvicorn.run(app, host= "0.0.0.0", port= 8000)