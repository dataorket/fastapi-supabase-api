# main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import feedparser
from dotenv import load_dotenv

# Load .env
load_dotenv()

app = FastAPI(title="FastAPI + Supabase RSS API")

# --------------------------
# Supabase credentials
# --------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Please set SUPABASE_URL and SUPABASE_KEY in environment variables!")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

RSS_FEED = "https://www.infomigrants.net/en/rss/all.xml"

# --------------------------
# Article data model
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
# AI-based classification
# --------------------------
def classify_article_ai(title: str, description: str):
    text = f"{title} {description}".lower()
    scores = {
        "Politics": 0.0,
        "Economy": 0.0,
        "Integration": 0.0,
        "Life in Germany": 0.0
    }

    if any(word in text for word in ["government", "election", "policy", "politics"]):
        scores["Politics"] += 0.15868
    if any(word in text for word in ["economy", "business", "market", "finance"]):
        scores["Economy"] += 0.32741
    if any(word in text for word in ["immigration", "refugee", "integration"]):
        scores["Integration"] += 0.22746
    if any(word in text for word in ["germany", "berlin", "munich", "life"]):
        scores["Life in Germany"] += 0.28643

    category = max(scores, key=scores.get)
    return category, scores

# --------------------------
# Check if article exists (dedup)
# --------------------------
async def article_exists(article_url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/articles",
            params={"url": f"eq.{article_url}", "select": "id"},
            headers=HEADERS,
            timeout=10
        )
        resp.raise_for_status()
        return len(resp.json()) > 0

# --------------------------
# POST single article
# --------------------------
@app.post("/articles")
async def post_article(article: Article):
    if await article_exists(article.url):
        return {"message": "⚠️ Duplicate article skipped", "url": article.url}

    async with httpx.AsyncClient() as client:
        payload = {k: v for k, v in article.dict().items() if v is not None}
        resp = await client.post(
            f"{SUPABASE_URL}/functions/v1/articles-insert",
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()

# --------------------------
# GET all articles
# --------------------------
@app.get("/articles")
def get_articles():
    try:
        resp = httpx.get(
            f"{SUPABASE_URL}/functions/v1/articles-get-api",
            headers=HEADERS,
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------
# Fetch RSS and insert one new article
# --------------------------
@app.post("/articles/fetch")
async def fetch_articles():
    feed = feedparser.parse(RSS_FEED)

    if not feed.entries:
        raise HTTPException(status_code=400, detail="RSS feed contains no entries")

    inserted_count = 0
    skipped_count = 0

    for entry in feed.entries:
        url = entry.get("link")
        if await article_exists(url):
            skipped_count += 1
            continue

        # Classify with AI
        category, category_scores = classify_article_ai(
            entry.get("title", ""), entry.get("description", "")
        )

        new_article = Article(
            feed_url=RSS_FEED,
            title=entry.get("title", "No title"),
            url=url,
            author=entry.get("author"),
            published=str(entry.get("published", None)),
            description=str(entry.get("description", None)),
            summary=str(entry.get("summary", None)),
            category=category,
            category_scores=category_scores
        )

        await post_article(new_article)
        inserted_count += 1
        break  # Insert only 1 new article

    return {
        "inserted": inserted_count,
        "skipped_duplicates": skipped_count
    }
