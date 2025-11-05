import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import httpx
import feedparser
from pydantic import BaseModel

load_dotenv()  # Loads .env when running locally

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment!")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

RSS_FEED = "https://www.infomigrants.net/en/rss/all.xml"

# --------------------------
# Data model for POST
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
# Helper: Check Supabase if article exists (dedup)
# --------------------------
async def article_exists(article_url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/articles",
            params={"url": f"eq.{article_url}", "select": "id"},
            headers=HEADERS,
            timeout=10
        )
        return len(resp.json()) > 0


# --------------------------
# POST new article
# --------------------------
@app.post("/articles")
async def post_article(article: Article):
    # Dedup check
    if await article_exists(article.url):
        return {"message": "⚠️ Duplicate article skipped", "url": article.url}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/functions/v1/articles-insert",
            headers=HEADERS,
            json={k: v for k, v in article.dict().items() if v is not None},
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()


# --------------------------
# GET articles from Supabase
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
# Fetch from RSS feed and insert only non-duplicates
# --------------------------
@app.post("/articles/fetch")
async def fetch_articles():
    feed = feedparser.parse(RSS_FEED)

    if not feed.entries:
        raise HTTPException(status_code=400, detail="RSS feed contains no entries")

    inserted_count = 0
    skipped_count = 0

    for entry in feed.entries[:5]:  # fetch first 5
        url = entry.get("link")

        if await article_exists(url):
            skipped_count += 1
            continue

        new_article = Article(
            feed_url=RSS_FEED,
            title=entry.get("title"),
            url=url,
            author=entry.get("author", None),
            published=str(entry.get("published", None)),
            description=str(entry.get("description", None)),
            summary=str(entry.get("summary", None)),
            category="rss",
            category_scores={"rss": 1.0},
        )

        await post_article(new_article)
        inserted_count += 1

    return {
        "inserted": inserted_count,
        "skipped_duplicates": skipped_count
    }
