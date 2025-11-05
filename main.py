import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load .env locally (ignored on Render)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("Please set DATABASE_URL in environment variables!")

# Parse DATABASE_URL
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

@app.get("/")
def home():
    return {"message": "✅ FastAPI is working on Render!"}


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


@app.get("/articles")
def get_articles(limit: int = 5):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM public.articles ORDER BY published DESC LIMIT %s;", (limit,)
    )
    articles = cur.fetchall()
    cur.close()
    conn.close()
    return {"articles": articles}


@app.post("/articles")
def post_article(article: Article):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO public.articles 
            (feed_url, title, url, author, published, description, summary, category, category_scores)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (url) DO NOTHING
            """,
            (
                article.feed_url,
                article.title,
                article.url,
                article.author,
                article.published,
                article.description,
                article.summary,
                article.category,
                article.category_scores
            )
        )
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert failed: {e}")
    finally:
        cur.close()
        conn.close()
    return {"message": "✅ Article inserted (if not duplicate)"}
