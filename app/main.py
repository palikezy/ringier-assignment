from fastapi import FastAPI

from app.routers.accu_weather import router as accu_weather_router

app = FastAPI(docs_url="/")
app.include_router(accu_weather_router, prefix="/accu_weather")
