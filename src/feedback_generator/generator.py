from collections import Counter
from g4f.client import Client
import json


def generate_summary(aspects_results):
    # Считаем аспекты
    pos_counter = Counter()
    neg_counter = Counter()

    total_count = len(aspects_results)  # можно изменить в зависимости от формата данных

    for review in aspects_results:
        pos_aspects = review.get("Достоинства", "")
        if pos_aspects != "не выявлены":
            pos_counter.update(pos_aspects.split(", "))

        neg_aspects = review.get("Недостатки", "")
        if neg_aspects != "не обнаружены":
            neg_counter.update(neg_aspects.split(", "))

    # ✅ Топ 3
    top_pos = pos_counter.most_common(3)
    top_neg = neg_counter.most_common(3)

    # ✅ Инфографика
    insights = []

    for aspect, count in top_pos:
        percent = int(count / total_count * 100)
        insights.append(f"{percent}% покупателей отмечают, что у товара «{aspect}»")

    for aspect, count in top_neg:
        percent = int(count / total_count * 100)
        insights.append(f"{percent}% жалуются, что у товара «{aspect}»")

    summary_input = {
        "положительные_аспекты": top_pos,
        "отрицательные_аспекты": top_neg,
        "всего_отзывов": total_count
    }

    # Генерация с помощью GPT
    client = Client()

    pos_str = ", ".join([f"{a} ({c})" for a, c in top_pos]) if top_pos else "нет"
    neg_str = ", ".join([f"{a} ({c})" for a, c in top_neg]) if top_neg else "нет"

    prompt = (
        f"По результатам анализа {total_count} отзывов:\n"
        f"Положительные аспекты: {pos_str}.\n"
        f"Отрицательные аспекты: {neg_str}.\n\n"
        "Составь единый агрегированный отзыв. Отзыв должен звучать живо и естественно, как будто его написал реальный человек. "
        "Не пиши списки, не используй формальный стиль. Укажи, что людям нравится, а что нет."
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