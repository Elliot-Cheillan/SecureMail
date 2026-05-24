import datetime
from .constants import spoofing_substitutions_dict
from rapidfuzz import process, distance
import numpy as np
import ipaddress
from gibberish_detector import detector, serializer
import os
from feature_engineering.config import GIBBERISH_PATH
import json


def convert_date_to_obj(
    date,
):  # idk if there is a function to convert string to date, but in the db the dates have 1 format so it's easy to convert
    if date == "Unknown":
        return date
    try:
        date_obj = date.split("-")
        year = int(date_obj[0])
        month = int(date_obj[1])
        day = int(date_obj[2])
        return datetime.datetime(year, month, day)
    except:
        return "Format Problem"


def convert_time_to_obj(time):  # same as above
    if time == "Unknown":
        return time
    try:
        time_obj = time.split(":")
        hour = int(time_obj[0])
        minute = int(time_obj[1])
        second = int(time_obj[2])
        return datetime.time(hour, minute, second, 0)
    except:
        return "Format Problem"


def string_substitutions_spoof(text):
    text.lower().strip()
    all_substitutions = [text]
    for k, v in spoofing_substitutions_dict.items():
        if k in text:
            all_substitutions.append(text.replace(k, v))
    return all_substitutions


def get_best_jaro_score(word_list, json_iterable):
    if not word_list or not json_iterable:
        return 0.0

    result = process.cdist(
        word_list, json_iterable, scorer=distance.JaroWinkler.similarity, workers=-1
    )

    return np.max(result)  # best match


def is_ipadress(ip):
    try:
        ipaddress.ip_address(ip)
        return 1
    except ValueError:
        return 0


with open(os.path.join(GIBBERISH_PATH, "gibberish_model.json")) as f:
    model = serializer.deserialize(json.load(f))

Detector = detector.Detector(model, 4.0)
