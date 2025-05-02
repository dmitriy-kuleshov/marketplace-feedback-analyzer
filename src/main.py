from fastapi import FastAPI, Request
from src.feedback_analyzer.data_cleaner import clean_data
from src.feedback_analyzer.sentiment_analyzer import analyze_reviews_with_sentiment
from src.feedback_analyzer.aspects_analyzer import analyze_aspects
from src.feedback_generator.generator import generate_summary
from src.models import ReviewsInput

app = FastAPI()

@app.get("/")
def ping():
    return {"status": "OK"}

@app.post("/analyze/")
def analyze_feedback(input_data: ReviewsInput):
    reviews = [review.model_dump() for review in input_data.root]

    cleaned = clean_data(reviews)["filtered"]
    sentiment_results = analyze_reviews_with_sentiment(cleaned)["reviews"]
    aspects_results = analyze_aspects(sentiment_results)
    final_output = generate_summary(aspects_results)

    return final_output
