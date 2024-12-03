from fastapi import FastAPI

from app.routers.accu_weather import router as accu_weather_router
from app.routers.open_meteo import router as open_meteo_router

app = FastAPI(docs_url="/")
app.include_router(accu_weather_router, prefix="/accu_weather")
app.include_router(open_meteo_router, prefix="/open_meteo")
