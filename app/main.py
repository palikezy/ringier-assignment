import json
import re
from datetime import date
from enum import StrEnum

import httpx
from fastapi import FastAPI, HTTPException
from ollama import AsyncClient
from pydantic import BaseModel

from .config import settings

app = FastAPI(docs_url="/")

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

type JsonType = dict[str, JsonType] | list[JsonType] | str | float | int | bool | None


def clean_data(data: JsonType) -> JsonType:
    if isinstance(data, dict):
        return {PASCAL_CASE_PATTERN.sub(" ", k): clean_data(v) for k, v in data.items() if k not in OMITTED_KEYS}
    if isinstance(data, list):
        return [clean_data(item) for item in data]
    return data


class Style(StrEnum):
    factual = "factual"
    tabloid = "tabloid"


STYLE_MAPPING: dict[Style, str] = {
    Style.factual: "factual and brief",
    Style.tabloid: "tabloid and dramatic",
}


class Locale(StrEnum):
    en = "en-gb"
    sk = "sk-sk"


LANGUAGE_MAPPING: dict[Locale, str] = {
    Locale.en: "english",
    Locale.sk: "slovak",
}


class ResponseModel(BaseModel):
    title: str
    perex: str
    text: str
    location: str
    locale: Locale
    style: Style


@app.get("/weather/forecast_today", responses={404: {"description": "Location not found"}})
async def weather_forecast_today(
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
    forecast_json = json.dumps(forecast_cleaned, indent=4)

    prompt = (
        f"Write an article in {LANGUAGE_MAPPING[locale]} language about today's weather forecast, "
        f"use {STYLE_MAPPING[style]} style, "
        f"respond in plain text, "
        # f"generate the article's title on the first line, "
        # f"generate the article's lead paragraph on the second line, "
        # f"generate the article's body starting with third line, "
        f"do not annotate article parts, "
        f"use the following JSON metadata as a source of information:\n\n{forecast_json}\n"
    )

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


@app.get("/weather/forecast_history", responses={404: {"description": "Location not found"}})
async def weather_forecast_history(
    forecast_date: date,
    location: str | None = None,
    locale: Locale | None = None,
    style: Style | None = None,
) -> list[dict]:
    # TODO: Query DB?
    return []
