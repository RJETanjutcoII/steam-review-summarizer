from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    appid: int = Field(..., description="Steam App ID, e.g. 730 for CS2")
    max_reviews: int = Field(40, ge=1, le=200, description="Max number of reviews to fetch")
    max_length: int = Field(150, ge=32, le=512, description="Max length of summary")
    min_length: int = Field(50, ge=10, le=256, description="Min length of summary")


class SummarizeResponse(BaseModel):
    appid: int
    review_count: int
    summary: str