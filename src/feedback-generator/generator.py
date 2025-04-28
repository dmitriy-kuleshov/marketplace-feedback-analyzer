from collections import Counter

from g4f.client import Client
import json

# ✅ Загружаем отзывы
with open("../feedback-analyzer/positive_reviews.json", "r", encoding="utf-8") as f_pos:
    positive_data = json.load(f_pos)

with open("../feedback-analyzer/negative_reviews.json", "r", encoding="utf-8") as f_neg:
    negative_data = json.load(f_neg)

# ✅ Считаем аспекты
pos_counter = Counter()
neg_counter = Counter()
total_count = len(positive_data) + len(negative_data)

for review in positive_data:
    aspects = review.get("Достоинства", "")
    if aspects != "не выявлены":
        pos_counter.update(aspects.split(", "))

for review in negative_data:
    aspects = review.get("Недостатки", "")
    if aspects != "не обнаружены":
        neg_counter.update(aspects.split(", "))

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


def ask_gpt(pos_aspects, neg_aspects, total_count) -> str:
    client = Client()
    pos_str = ", ".join([f"{a} ({c})" for a, c in pos_aspects]) if pos_aspects else "нет"
    neg_str = ", ".join([f"{a} ({c})" for a, c in neg_aspects]) if neg_aspects else "нет"

    prompt = (
        f"По результатам анализа {total_count} отзывов:\n"
        f"Положительные аспекты: {pos_str}.\n"
        f"Отрицательные аспекты: {neg_str}.\n\n"
        "Составь единый агрегированный отзыв. Отзыв должен звучать живо и естественно, как будто его написал реальный человек. "
        "Не пиши списки, не используй формальный стиль. Укажи, что людям нравится, а что нет."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты AI, который составляет сводные отзывы на основе анализа."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        web_search=False
    )
    return response.choices[0].message.content


summary_text = ask_gpt(top_pos, top_neg, total_count)

# ✅ Сохраняем результат
final_output = {
    "Сводный отзыв": summary_text,
    "Ключевые наблюдения": insights
}

with open("aggregated_review_summary.json", "w", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

print("✅ Итог сохранён в aggregated_review_summary.json")
