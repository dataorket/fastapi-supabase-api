import os
from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --------------------------
# Data model for POST request
# --------------------------
class Article(BaseModel):
    feed_url: str | None = None
    title: str
    url: str
    author: str | None = None
    published: str | None = None
    description: str | None = None
    summary: str | None = None
    category: str | None = None
    category_scores: dict | None = None

# --------------------------
# GET articles via Supabase Edge Function
# --------------------------
@app.get("/articles")
def get_articles():
    try:
        resp = httpx.get(f"{SUPABASE_URL}/functions/v1/articles-get-api", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from Supabase: {e.response.text}")

# --------------------------
# POST new article via Supabase Edge Function
# --------------------------
@app.post("/articles")
def post_article(article: Article):
    try:
        resp = httpx.post(
            f"{SUPABASE_URL}/functions/v1/articles-post-api",
            headers=HEADERS,
            json=article.dict(),
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from Supabase: {e.response.text}")
