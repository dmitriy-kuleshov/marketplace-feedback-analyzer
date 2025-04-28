import torch
import transformers
import numpy as np
import re
import json

MODEL_NAME = "blanchefort/rubert-base-cased-sentiment"
tokenizer = transformers.AutoTokenizer.from_pretrained(MODEL_NAME)
model = transformers.AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

def preprocess_text(review):
    parts = []
    if review.get("productValuation"):
        parts.append(f"Оценка: {review['productValuation']} из 5.")
    if review["text"]:
        parts.append(review["text"])
    if review["pros"]:
        parts.append(f"Плюсы: {review['pros']}")
    if review["cons"]:
        parts.append(f"Минусы: {review['cons']}")
    return " ".join(parts).strip()

def rule_based_boost(text, sentiment, scores):
    text_lower = text.lower()

    negative_keywords = [
        r"не\s+рекомендую", r"не\s+советую", r"полная.+шляпа",
        r"все.+вранье", r"сломался", r"не\s+работает", r"развалился", r"обман",
        r"покупайте.+скупой.+дважды", r"говно", r"очень плохо", r"очень плохое",
        r"отвратительно", r"отвратительное", r"отвратительный", r"отвратительная",
        r"рваный", r"ужас", r"жесть", r"кошмар", r"разочарование", r"не стоящий",
        r"ужасный", r"убогий", r"не работает", r"не включается", r"не отвечает",
        r"не работает корректно", r"неисправный", r"часто зависает", r"перегревается",
        r"плохо сделано", r"не соответствует описанию", r"не оправдал ожиданий",
        r"плохое качество", r"низкое качество", r"хлипкий", r"бракованный",
        r"не стоит своих денег", r"не соответствует рекламе", r"обман", r"надувательство",
        r"развод", r"не покупайте", r"ужасный опыт"
    ]

    positive_keywords = [
        r"всё отлично", r"работает хорошо", r"супер", r"советую", r"рекомендую",
        r"прекрасно", r"очень доволен", r"идеально", r"качество.+отличное", r"понравился",
        r"нравится", r"классно", r"классный", r"классное", r"топ", r"топово", r"топовый",
        r"топовое", r"топовая", r"классная", r"суперски", r"суперский", r"суперская",
        r"суперское", r"идеальный", r"отличный", r"в восторге", r"замечательно", r"потрясающе",
        r"восхищён", r"удивительно", r"шикарно", r"бомбически", r"огонь", r"невероятно",
        r"отлично", r"цена/качество на высоте", r"не пожалел", r"без нареканий", r"превосходно",
        r"удобный", r"качественный", r"легкий в использовании", r"практичный", r"хороший"
    ]

    if any(re.search(pat, text_lower) for pat in negative_keywords):
        return "негатив"

    if any(re.search(pat, text_lower) for pat in positive_keywords):
        return "позитив"

    return sentiment

def analyze_sentiment(text):
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        output = model(**tokens)

    scores = torch.nn.functional.softmax(output.logits, dim=-1).numpy()[0]
    num_labels = len(scores)

    if num_labels == 2:
        labels = ["негатив", "позитив"]
    else:
        labels = ["негатив", "нейтральный", "позитив"]

    confidence = np.max(scores)

    if confidence < 0.5:
        sentiment = "нейтральный"
    else:
        sentiment = labels[np.argmax(scores)]

    if num_labels == 3:
        delta = scores[2] - scores[0]
        if delta > 0.15:
            sentiment = "позитив"
        elif delta < -0.15:
            sentiment = "негатив"
        else:
            sentiment = "нейтральный"

    return sentiment, scores

def adjust_sentiment_based_on_rating(sentiment, rating):
    if rating in [4, 5]:
        if sentiment == "негатив":
            sentiment = "нейтральный"
        elif sentiment == "нейтральный":
            sentiment = "позитив"
    elif rating == 3:
        sentiment = "нейтральный"
    elif rating in [1, 2]:
        if sentiment == "позитив":
            sentiment = "нейтральный"
        elif sentiment == "нейтральный":
            sentiment = "негатив"
    return sentiment

# Читаем JSON с отзывами
with open("filtered_data.json", "r", encoding="utf-8") as file:
    reviews = json.load(file)

results = []
for i, review in enumerate(reviews, start=1):
    review["review_number"] = i  # добавляем номер отзыва

    full_text = preprocess_text(review)
    rating = review.get("productValuation", 3)

    if full_text:
        sentiment, scores = analyze_sentiment(full_text)
        original_sentiment = sentiment
        sentiment = rule_based_boost(full_text, sentiment, scores)
        sentiment = adjust_sentiment_based_on_rating(sentiment, rating)

        review["sentiment"] = sentiment
        review["rule_based_override"] = f"{original_sentiment} → {sentiment}" if sentiment != original_sentiment else None

        num_labels = len(scores)
        if num_labels == 2:
            review["sentiment_scores"] = {
                "негатив": round(scores[0].item(), 3),
                "позитив": round(scores[1].item(), 3),
            }
        else:
            review["sentiment_scores"] = {
                "негатив": round(scores[0].item(), 3),
                "нейтральный": round(scores[1].item(), 3),
                "позитив": round(scores[2].item(), 3),
            }
    else:
        review["sentiment"] = "не определено"
        review["sentiment_scores"] = None

    # Переставляем review_number в начало
    ordered_review = {
        "review_number": review["review_number"],
        **{k: v for k, v in review.items() if k != "review_number"}
    }

    results.append(ordered_review)

# Сохраняем результаты
with open("reviews_with_sentiment.json", "w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=4)

print("Анализ тональности завершен! Результаты сохранены в reviews_with_sentiment.json")
