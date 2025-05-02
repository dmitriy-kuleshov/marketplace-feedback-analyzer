import json


def is_informative(review):
    filled_fields = sum(bool(review.get(key)) for key in ["text", "pros", "cons"])
    total_length = sum(len(review.get(key, "").strip()) for key in ["text", "pros", "cons"])
    return filled_fields > 1 and total_length >= 50


def clean_data(data: list) -> dict:
    filtered_data = [review for review in data if is_informative(review)]
    return {"filtered": filtered_data}


# if __name__ == "__main__":
#     import json
#
#     with open("../feedback_parser/30.json", "r", encoding="utf-8") as file:
#         raw_data = json.load(file)
#
#     result = clean_data(raw_data)
#     with open("filtered_data.json", "w", encoding="utf-8") as file:
#         json.dump(result["filtered"], file, indent=4, ensure_ascii=False)
#
#     print("Фильтрация завершена! Результат сохранён в filtered_data.json")
