from datetime import date
from enum import StrEnum

import httpx
import ollama
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import settings
from app.dependencies import JsonType, Locale, ResponseModel, Style, create_prompt

router = APIRouter()


class Coordinates(BaseModel):
    lat: float
    lon: float


class Location(StrEnum):
    ulaanbaatar = "Ulaanbaatar"
    bratislava = "Bratislava"
    prague = "Prague"


LOCATION_MAPPING = {
    Location.ulaanbaatar: Coordinates(lat=47.9077, lon=106.8832),
    Location.bratislava: Coordinates(lat=48.1482, lon=17.1067),
    Location.prague: Coordinates(lat=50.088, lon=14.4208),
}


def clean_data(data: JsonType) -> dict[str, str]:
    units = data["daily_units"]
    result = {" ".join(key.split("_")): f"{value} {units[key]}" for key, value in data["daily"].items()}
    result["date"] = data["daily"]["time"]
    del result["time"]
    return result


def clean_data_history(data: JsonType) -> dict[str, str]:
    units = data["daily_units"]
    result = {" ".join(key.split("_")): f"{value[0]} {units[key]}" for key, value in data["daily"].items()}
    result["date"] = data["daily"]["time"][0]
    del result["time"]
    return result


@router.get("/forecast_1_day")
def forecast_1_day(
    location: Location = Location.ulaanbaatar,
    locale: Locale = Locale.en,
    style: Style = Style.tabloid,
) -> ResponseModel:
    # TODO: Make timezone customizable
    text = get_forecast_1_day_text(
        LOCATION_MAPPING[location],
        "Europe/Berlin",
        locale,
        style,
    )
    return ResponseModel(
        title="in text probably :(",
        perex="in text probably :(",
        text=text,
        location=location,
        locale=locale,
        style=style,
    )


@router.get("/forecast_1_day_by_coordinates")
def forecast_1_day_by_coordinates(
    coordinates: Coordinates = Depends(),
    timezone: str = "Europe/Berlin",
    locale: Locale = Locale.en,
    style: Style = Style.tabloid,
) -> dict:
    # TODO: Make timezone customizable
    text = get_forecast_1_day_text(
        coordinates,
        timezone,
        locale,
        style,
    )
    return ResponseModel(
        title="in text probably :(",
        perex="in text probably :(",
        text=text,
        location="custom",
        locale=locale,
        style=style,
    )


@router.get("/forecast_history")
def forecast_history(
    forecast_date: date,
    location: Location = Location.ulaanbaatar,
    locale: Locale = Locale.en,
    style: Style = Style.tabloid,
) -> ResponseModel:
    # TODO: Make timezone customizable
    text = get_forecast_history_text(
        LOCATION_MAPPING[location],
        "Europe/Berlin",
        locale,
        style,
        forecast_date,
    )
    return ResponseModel(
        title="in text probably :(",
        perex="in text probably :(",
        text=text,
        location=location,
        locale=locale,
        style=style,
    )


@router.get("/forecast_history_by_coordinates")
def forecast_history_by_coordinates(
    forecast_date: date,
    coordinates: Coordinates = Depends(),
    timezone: str = "Europe/Berlin",
    locale: Locale = Locale.en,
    style: Style = Style.tabloid,
) -> ResponseModel:
    # TODO: Make timezone customizable
    text = get_forecast_history_text(
        coordinates,
        timezone,
        locale,
        style,
        forecast_date,
    )
    return ResponseModel(
        title="in text probably :(",
        perex="in text probably :(",
        text=text,
        location="custom",
        locale=locale,
        style=style,
    )


def get_forecast_1_day_text(
    coordinates: Coordinates,
    timezone: str,
    locale: Locale,
    style: Style,
) -> str:
    response = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": coordinates.lat,
            "longitude": coordinates.lon,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "sunrise",
                "sunset",
                "daylight_duration",
                "sunshine_duration",
                "uv_index_max",
                "precipitation_sum",
                "rain_sum",
                "snowfall_sum",
                "precipitation_hours",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "wind_direction_10m_dominant",
            ],
            "timezone": timezone,
            "forecast_days": 1,
        },
    )
    data = clean_data(response.raise_for_status().json())
    prompt = create_prompt(locale, style, data)
    response = ollama.generate(model=settings.llm_model, prompt=prompt, stream=False)
    return response["response"]


def get_forecast_history_text(
    coordinates: Coordinates,
    timezone: str,
    locale: Locale,
    style: Style,
    forecast_date: date,
) -> str:
    response = httpx.get(
        "https://historical-forecast-api.open-meteo.com/v1/forecast",
        params={
            "latitude": coordinates.lat,
            "longitude": coordinates.lon,
            "start_date": forecast_date.isoformat(),
            "end_date": forecast_date.isoformat(),
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "sunrise",
                "sunset",
                "daylight_duration",
                "sunshine_duration",
                "uv_index_max",
                "precipitation_sum",
                "rain_sum",
                "snowfall_sum",
                "precipitation_hours",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "wind_direction_10m_dominant",
            ],
            "timezone": timezone,
        },
    )
    data = clean_data(response.raise_for_status().json())
    prompt = create_prompt(locale, style, data)
    response = ollama.generate(model=settings.llm_model, prompt=prompt, stream=False)
    return response["response"]
