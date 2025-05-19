from collections import Counter
from g4f.client import Client
import json


def generate_summary(aspects_results):
    from collections import Counter

    # Словарь соответствий: "общий_аспект": ("позитивная формулировка", "негативная формулировка")
    aspect_pairs = {
        "Доставка": ("Хорошая доставка", "Плохая доставка"),
        "Удобство": ("Удобство в использовании", "Неудобный интерфейс"),
        "Соответствие описанию": ("Соответствует описанию", "Не соответствует описанию"),
        "Качество": ("Высокое качество", "Низкое качество товара"),
        "Комплектация": ("Полная комплектация", "Неполная комплектация"),
        "Цена": ("Приемлемая цена", "Завышенная цена"),
        "Эстетика/внешний вид": ("Приятный внешний вид", "Плохой внешний вид")
    }


    SIGNIFICANCE_THRESHOLD = 10  # минимальный процент для включения в инсайты

    pos_counter = Counter()
    neg_counter = Counter()
    total_count = len(aspects_results)

    for review in aspects_results:
        pos_aspects = review.get("Достоинства", "")
        if pos_aspects != "не выявлены":
            pos_counter.update(pos_aspects.split(", "))

        neg_aspects = review.get("Недостатки", "")
        if neg_aspects != "не обнаружены":
            neg_counter.update(neg_aspects.split(", "))

    # Выводим только перевешивающие и частотные аспекты
    insights = []

    for general_aspect, (pos_name, neg_name) in aspect_pairs.items():
        pos_count = pos_counter.get(pos_name, 0)
        neg_count = neg_counter.get(neg_name, 0)

        if pos_count > neg_count:
            percent = int(pos_count / total_count * 100)
            if percent >= SIGNIFICANCE_THRESHOLD:
                insights.append(f"{percent}% покупателей отмечают, что у товара «{pos_name}»")
        elif neg_count > pos_count:
            percent = int(neg_count / total_count * 100)
            if percent >= SIGNIFICANCE_THRESHOLD:
                insights.append(f"{percent}% жалуются, что у товара «{neg_name}»")
        # если равны — не добавляем ни один

    # Подготовка данных для генерации текста
    filtered_pos = {
        pos_name: pos_counter[pos_name]
        for general_aspect, (pos_name, neg_name) in aspect_pairs.items()
        if pos_counter[pos_name] > neg_counter[neg_name] and int(pos_counter[pos_name] / total_count * 100) >= SIGNIFICANCE_THRESHOLD
    }

    filtered_neg = {
        neg_name: neg_counter[neg_name]
        for general_aspect, (pos_name, neg_name) in aspect_pairs.items()
        if neg_counter[neg_name] > pos_counter[pos_name] and int(neg_counter[neg_name] / total_count * 100) >= SIGNIFICANCE_THRESHOLD
    }

    # Топ аспекты по частоте (можно ограничить, например, 3)
    top_pos = Counter(filtered_pos).most_common(3)
    top_neg = Counter(filtered_neg).most_common(3)
    client = Client()

    pos_str = ", ".join([f"{a} ({c})" for a, c in top_pos]) if top_pos else "нет"
    neg_str = ", ".join([f"{a} ({c})" for a, c in top_neg]) if top_neg else "нет"

    prompt = (
        f"По результатам анализа {total_count} отзывов:\n"
        f"Положительные аспекты: {pos_str}.\n"
        f"Отрицательные аспекты: {neg_str}.\n\n"
        "Составь единый агрегированный отзыв. Отзыв должен звучать живо и естественно, как будто его написал реальный человек. "
        "Не пиши списки, не используй формальный стиль. Укажи, что людям нравится, а что нет. Максимальный объём отзыва 35 слов."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": "Ты AI, который составляет сводные отзывы на основе анализа."
        }, {
            "role": "user",
            "content": prompt
        }],
        web_search=False
    )

    return {
        "Сводный отзыв": response.choices[0].message.content,
        "Ключевые наблюдения": insights
    }
