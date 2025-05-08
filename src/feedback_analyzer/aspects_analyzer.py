from fastapi import FastAPI, Request
from src.feedback_analyzer.data_cleaner import clean_data
from src.feedback_analyzer.sentiment_analyzer import analyze_reviews_with_sentiment
from src.feedback_analyzer.aspects_analyzer import analyze_aspects
from src.feedback_generator.generator import generate_summary
from src.models import ReviewsInput
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def ping():
    return {"status": "OK"}

@app.post("/analyze/")
def analyze_feedback(input_data: ReviewsInput):
    reviews = [review.model_dump() for review in input_data.root]

    print("Пришло от клиента:", len(reviews))

    sentiment_results = analyze_reviews_with_sentiment(reviews)["reviews"]
    cleaned = clean_data(reviews)["filtered"]
    print("После clean_data:", len(cleaned))

    cleaned_ids = {r["createdDate"] for r in cleaned}
    cleaned_sentiments = [r for r in sentiment_results if r["createdDate"] in cleaned_ids]

    aspects_results = analyze_aspects(cleaned_sentiments)
    final_output = generate_summary(aspects_results)

    sentiment_distribution = count_sentiment_by_period(sentiment_results)

    return {
        "summary": final_output["Сводный отзыв"],
        "insights": final_output["Ключевые наблюдения"],
        "sentiment_distribution": sentiment_distribution
    }

def count_sentiment_by_period(reviews: list[dict]) -> dict:
    now = datetime.utcnow()
    one_week_ago = now - timedelta(days=7)
    one_month_ago = now - timedelta(days=30)
    def to_naive(dt: datetime) -> datetime:
        return dt.replace(tzinfo=None)

    def filter_and_count(start_date):
        counter = {"позитив": 0, "нейтральный": 0, "негатив": 0}
        for review in reviews:
            date = review.get("createdDate")
            sentiment = review.get("sentiment")
            if not date or not sentiment:
                continue
            if isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date.replace("Z", "+00:00"))
                except:
                    continue
            date = to_naive(date)
            if date >= start_date:
                if sentiment in counter:
                    counter[sentiment] += 1
        return counter

    return {
        "week": filter_and_count(one_week_ago),
        "month": filter_and_count(one_month_ago),
        "all": filter_and_count(datetime.min)
    }