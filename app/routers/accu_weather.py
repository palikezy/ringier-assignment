import json
import re

import httpx
from fastapi import APIRouter, HTTPException
from ollama import AsyncClient

from app.config import settings
from app.dependencies import JsonType, Locale, ResponseModel, Style, create_prompt

router = APIRouter()

PASCAL_CASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")
OMITTED_KEYS = {
    "EpochDate",
    "EpochRise",
    "EpochSet",
    "CategoryValue",
    "Icon",
    "IconPhrase",
    "UnitType",
    "WetBulbTemperature",
    "WetBulbGlobeTemperature",
    "Sources",
    "MobileLink",
    "Link",
}


def clean_data(data: JsonType) -> JsonType:
    if isinstance(data, dict):
        return {PASCAL_CASE_PATTERN.sub(" ", k): clean_data(v) for k, v in data.items() if k not in OMITTED_KEYS}
    if isinstance(data, list):
        return [clean_data(item) for item in data]
    return data


@router.get("/forecast_1_day", responses={404: {"description": "Location not found"}})
async def forecast_1_day(
    location: str,
    locale: Locale = Locale.en,
    style: Style = Style.tabloid,
) -> ResponseModel:
    async with httpx.AsyncClient(params={"apikey": settings.forecast_api_key}) as client:
        # TODO: Verify response structures?

        # Obtain location key
        response = await client.get(
            "http://dataservice.accuweather.com/locations/v1/search",
            params={"q": location, "language": locale},
        )
        response.raise_for_status()
        locations = response.json()
        if not locations:
            raise HTTPException(status_code=404, detail="Location not found")
        location_key = locations[0]["Key"]
        location_name = locations[0]["EnglishName"]

        # Obtain forecast
        response = await client.get(
            f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}",
            params={
                # "language": locale,  # Do not confuse model with multilanguage JSON!
                "details": settings.forecast_detail,
                "metric": settings.forecast_metric,
            },
        )
        response.raise_for_status()
        forecast = response.json()

    forecast_cleaned = clean_data(forecast["DailyForecasts"][0])
    forecast_cleaned["Location"] = "Bratislava"

    prompt = create_prompt(locale, style, forecast_cleaned)
    ollama_client = AsyncClient(host=settings.ollama_url)
    response = await ollama_client.generate(model=settings.llm_model, prompt=prompt, stream=False)
    text = response["response"]

    return ResponseModel(
        title="in text probably :(",
        perex="in text probably :(",
        text=text,
        location=location,
        locale=locale,
        style=style,
    )
