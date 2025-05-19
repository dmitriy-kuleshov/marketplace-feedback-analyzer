import json


def is_informative(review):
    filled_fields = sum(bool(review.get(key)) for key in ["text", "pros", "cons"])
    total_length = sum(len(review.get(key, "").strip()) for key in ["text", "pros", "cons"])
    return filled_fields > 1 and total_length >= 25


def clean_data(data: list) -> dict:
    filtered_data = [review for review in data if is_informative(review)]
    return {"filtered": filtered_data}