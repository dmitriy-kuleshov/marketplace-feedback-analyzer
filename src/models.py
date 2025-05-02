from pydantic import BaseModel, RootModel
from typing import Optional
from datetime import datetime

class Review(BaseModel):
    text: str
    pros: Optional[str] = ""
    cons: Optional[str] = ""
    productValuation: Optional[int] = 0
    createdDate: Optional[datetime] = None

class ReviewsInput(RootModel[list[Review]]):
    pass
