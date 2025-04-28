import json

# Функция для проверки "пустых" и коротких отзывов
def is_informative(review):
    # Проверяем количество заполненных полей
    filled_fields = sum(bool(review[key]) for key in ["text", "pros", "cons"])

    # Считаем суммарную длину всех полей
    total_length = len(review["text"].strip()) + len(review["pros"].strip()) + len(review["cons"].strip())

    # Отбрасываем, если заполнено ≤ 1 поля или суммарная длина < 50 символов
    return filled_fields > 1 and total_length >= 50

# Читаем JSON
with open("../feedback-parser/10.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Фильтруем отзывы
filtered_data = [review for review in data if is_informative(review)]

# Записываем обратно
with open("filtered_data.json", "w", encoding="utf-8") as file:
    json.dump(filtered_data, file, indent=4, ensure_ascii=False)

print("Фильтрация завершена! Результат сохранён в filtered_data.json")