# main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import sys

# Optional: RSS fetching
import feedparser
from datetime import datetime

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not DATABASE_URL:
    raise SystemExit("Please set DATABASE_URL in environment variables!")

parsed = urlparse(DATABASE_URL)
DB_USER = parsed.username
DB_PASSWORD = parsed.password
DB_HOST = parsed.hostname
DB_PORT = parsed.port
DB_NAME = parsed.path.lstrip("/")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            sslmode="require",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

app = FastAPI()

# --------------------------
# Data model
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
# GET all articles
# --------------------------
@app.get("/articles")
def get_articles(limit: int = 5):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.articles ORDER BY published DESC LIMIT %s;", (limit,))
    articles = cur.fetchall()
    cur.close()
    conn.close()
    return {"articles": articles}

# --------------------------
# POST a new article
# --------------------------
@app.post("/articles")
def post_article(article: Article):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO public.articles 
            (feed_url, title, url, author, published, description, summary, category, category_scores)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (url) DO NOTHING
        """, (
            article.feed_url,
            article.title,
            article.url,
            article.author,
            article.published,
            article.description,
            article.summary,
            article.category,
            article.category_scores
        ))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert failed: {e}")
    finally:
        cur.close()
        conn.close()
    return {"message": "✅ Article inserted (if not duplicate)"}

# --------------------------
# RSS Fetcher
# --------------------------
def fetch_rss(feed_url: str):
    conn = get_db_connection()
    cur = conn.cursor()
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:5]:  # latest 5
        published_struct = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
        published = datetime(*published_struct[:6]) if published_struct else datetime.now()
        cur.execute("""
            INSERT INTO public.articles 
            (feed_url, title, url, author, published, description)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (url) DO NOTHING
        """, (
            feed_url,
            entry.get("title", ""),
            entry.get("link", ""),
            entry.get("author", None),
            published,
            entry.get("summary", entry.get("description", ""))
        ))
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Fetched and inserted top 5 articles from {feed_url}")

# --------------------------
# CLI support
# --------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fetch_rss":
        FEED_URL = sys.argv[2] if len(sys.argv) > 2 else "https://www.infomigrants.net/en/rss/all.xml"
        fetch_rss(FEED_URL)
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
