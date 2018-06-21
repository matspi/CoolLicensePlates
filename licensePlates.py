#!/usr/bin/env python3

import sys

import requests
from google.cloud import translate

REGIST_URL = r"https://www.berlin.de/daten/liste-der-kfz-kennzeichen/kfz-kennz-d.csv"

NUMBERS = (
    "null",
    "eins",
    "zwei",
    "drei",
    "vier",
    "fünf",
    "sechs",
    "sieben",
    "acht",
    "neun"
)

csvData = requests.get(REGIST_URL)
csvData.encoding = "utf-8"
PREFIXES = {k.lower(): v for k, v in (
    line.split(",")[0:2] for line in csvData.text.split("\r\n")[1:-1])} # first and last line contain garbage

translateClient = translate.Client()
languages = translateClient.get_languages()

result = {}


def findMatches(language, numbers):
    for idx in range(0, len(numbers)):
        foreignNumer = numbers[idx]
        if len(foreignNumer) > 5:
            continue
        for prefix in PREFIXES.keys():
            search = foreignNumer.partition(prefix)
            if search[0]:
                continue  # No prefix
            if len(search[2]) > 2 or len(search[2]) < 1:
                continue  # suffix too long or short
            if not all(ord(char) < 128 for char in search[2]):
                continue  # illegal characters
            if not language in result:
                result[language] = []
            result.get(language).append(
                (prefix.upper(), search[2].upper(), idx + 1, PREFIXES[prefix]))


for lang in languages:
    langCode = lang["language"]
    if langCode == "de":
        continue
    translated = [i["translatedText"].lower() for i in translateClient.translate(
        NUMBERS[1:], target_language=langCode, source_language="de")]
    findMatches(lang["name"], translated)

findMatches("German", NUMBERS[1:])

print("%d results" % len(result))

for lang in result:
    print("\n##", lang, "\n")
    for res in result[lang]:
        print(" - %s - %s %d* %s" % res)
