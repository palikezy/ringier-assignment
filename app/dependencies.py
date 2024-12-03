import json
from enum import StrEnum

from pydantic import BaseModel

type JsonType = dict[str, JsonType] | list[JsonType] | str | float | int | bool | None


class Locale(StrEnum):
    en = "en-gb"
    sk = "sk-sk"


class Style(StrEnum):
    factual = "factual"
    tabloid = "tabloid"


class ResponseModel(BaseModel):
    title: str
    perex: str
    text: str
    location: str
    locale: Locale
    style: Style


LANGUAGE_MAPPING: dict[Locale, str] = {
    Locale.en: "english",
    Locale.sk: "slovak",
}
STYLE_MAPPING: dict[Style, str] = {
    Style.factual: "factual and brief",
    Style.tabloid: "tabloid and dramatic",
}


def create_prompt(locale: Locale, style: Style, data: JsonType) -> str:
    data_json = json.dumps(data, indent=4)
    return (
        f"Write an article in {LANGUAGE_MAPPING[locale]} language about today's weather forecast, "
        f"use {STYLE_MAPPING[style]} style, "
        f"respond in plain text, "
        # f"generate the article's title on the first line, "
        # f"generate the article's lead paragraph on the second line, "
        # f"generate the article's body starting with third line, "
        f"do not annotate article parts, "
        f"use the following JSON metadata as a source of information:\n\n{data_json}\n"
    )
