import rapidfuzz
import json
import re

# --- Ключевые слова для аспектов ---
aspect_keywords = {
    "Качество товара": {
        "positive": [
            "качественный", "надежный", "прочный", "нормально сделан", "сделано хорошо",
            "сделан добротно", "не скрипит", "работает стабильно"
        ],
        "negative": [
            "сломался", "брак", "развалился", "хлипкий", "трещина", "некачественный",
            "разболтался", "шумит", "перестал работать", "бракованный"
        ]
    },
    "Комплектация": {
        "positive": [
            "всё в комплекте", "полный комплект", "насадки есть", "оснащение хорошее",
            "всё как заявлено"
        ],
        "negative": [
            "не положили", "не хватает", "отсутствует", "пустая коробка",
            "чего-то не хватает", "не доложили", "не тот комплект"
        ]
    },
    "Доставка": {
        "positive": [
            "пришло быстро", "пришел вовремя", "доставили раньше", "упакован хорошо",
            "всё целое", "упаковано отлично", "никаких повреждений", "доставка отличная",
            "привезли быстро", "доставка на уровне"
        ],
        "negative": [
            "ждал долго", "задержка", "упаковка повреждена", "мятая коробка",
            "сломали в доставке", "испорчена упаковка"
        ]
    },
    "Соответствие описанию": {
        "positive": [
            "соответствует описанию", "как в описании", "ожидания оправдались",
            "всё как заявлено", "совпадает с фото", "оригинал", "всё так, как описано"
        ],
        "negative": [
            "не соответствует", "не совпадает", "не такое", "вранье", "обман",
            "подделка", "в описании другое", "не как на фото"
        ]
    },
    "Цена": {
        "positive": [
            "дешево", "цена отличная", "доступный", "цена норм", "выгодно",
            "цена приемлемая", "дёшево и сердито", "своих денег стоит",
            "цена хорошая", "дешевле только даром"
        ],
        "negative": [
            "дорого", "переплата", "не стоит этих денег", "цена завышена",
            "расходы большие", "завышенная цена"
        ]
    },
    "Удобство": {
        "positive": [
            "удобный", "эргономичный", "лёгкий", "компактный", "в руке лежит хорошо",
            "прост в использовании", "интуитивно понятно"
        ],
        "negative": [
            "неудобный", "тяжелый", "непродуманный", "громоздкий", "не ложится в руку",
            "сложно использовать"
        ]
    },
    "Эстетика/внешний вид": {
        "positive": [
            "красивый", "симпатичный", "стильно выглядит", "дизайн приятный",
            "выглядит хорошо", "внешне нравится", "эстетика на уровне"
        ],
        "negative": [
            "уродливый", "дизайн отстой", "выглядит дёшево", "страшный",
            "внешне плохой", "неприятный внешний вид"
        ]
    }
}

# --- Формулировки аспектов ---
aspect_titles = {
    "Качество товара": {
        "positive": "Качество товара",
        "negative": "Низкое качество товара"
    },
    "Комплектация": {
        "positive": "Полная комплектация",
        "negative": "Неполная комплектация"
    },
    "Доставка": {
        "positive": "Хорошая доставка",
        "negative": "Плохая доставка"
    },
    "Соответствие описанию": {
        "positive": "Соответствие описанию",
        "negative": "Не соответствует описанию"
    },
    "Цена": {
        "positive": "Приемлемая цена",
        "negative": "Завышенная цена"
    },
    "Удобство": {
        "positive": "Удобство в использовании",
        "negative": "Неудобство в использовании"
    },
    "Эстетика/внешний вид": {
        "positive": "Приятный внешний вид",
        "negative": "Плохой внешний вид"
    }
}

# --- Бессмысленные фразы ---
useless_phrases = [
    r"все хорошо", r"доволен", r"понравилось", r"супер", r"отлично",
    r"ок", r"всё нравится", r"все устраивает", r"без нареканий", r"нареканий нет",
    r"норм"
]


def clean_phrases(text):
    text = text.lower()
    for phrase in useless_phrases:
        if re.search(phrase, text):
            return ""
    return text.strip()


# --- Сопоставление с аспектами ---
def extract_aspects(text):
    text = text.lower()
    found_pros = []
    found_cons = []

    words = re.findall(r"\w+", text)

    for aspect, polarity_map in aspect_keywords.items():
        for polarity, keywords in polarity_map.items():
            for kw in keywords:
                for word in words:
                    if rapidfuzz.fuzz.ratio(word, kw) >= 85 or rapidfuzz.fuzz.partial_ratio(kw, text) > 85:
                        if polarity == "positive":
                            found_pros.append(aspect_titles[aspect]["positive"])
                        elif polarity == "negative":
                            found_cons.append(aspect_titles[aspect]["negative"])
                        break
    return list(set(found_pros)), list(set(found_cons))


def get_aspect_from_title(title):
    for aspect, titles in aspect_titles.items():
        if title in titles.values():
            return aspect
    return None


def analyze_aspects(reviews):
    result_rows = []
    for review in reviews:
        text = review.get("text", "")
        pros_raw = clean_phrases(review.get("pros", ""))
        cons_raw = clean_phrases(review.get("cons", ""))

        if not pros_raw and not cons_raw and not text.strip():
            continue

        pros_text, cons_text = extract_aspects(text)
        pros_pros, cons_pros = extract_aspects(pros_raw)
        pros_cons, cons_cons = extract_aspects(cons_raw)

        pros_titles = pros_text + pros_pros + pros_cons
        cons_titles = cons_text + cons_pros + cons_cons

        pros_aspects = {get_aspect_from_title(title): title for title in pros_titles}
        cons_aspects = {get_aspect_from_title(title): title for title in cons_titles}

        conflicting_aspects = set(pros_aspects.keys()) & set(cons_aspects.keys())

        score = review.get("productValuation")
        if score in [1, 2]:
            for aspect in conflicting_aspects:
                pros_aspects.pop(aspect, None)
        elif score in [3, 4, 5]:
            for aspect in conflicting_aspects:
                cons_aspects.pop(aspect, None)

        final_pros = list(pros_aspects.values())
        final_cons = list(cons_aspects.values())

        imbalance_threshold = 1.5
        if len(final_cons) > 0 and len(final_pros) / len(final_cons) >= imbalance_threshold:
            final_cons = []
        elif len(final_pros) > 0 and len(final_cons) / len(final_pros) >= imbalance_threshold:
            final_pros = []

        pros_str = ", ".join(final_pros) if final_pros else "не выявлены"
        cons_str = ", ".join(final_cons) if final_cons else "не обнаружены"

        if pros_str == "не выявлены" and cons_str == "не обнаружены":
            continue

        result_rows.append({
            "Номер отзыва": review["review_number"],
            "Оценка": score,
            "Достоинства": pros_str,
            "Недостатки": cons_str,
            "Пример отзыва": text
        })

    return result_rows