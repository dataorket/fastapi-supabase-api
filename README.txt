FastAPI Supabase RSS API
========================

Overview
--------
A FastAPI application that:
- Fetches articles from RSS feeds.
- Inserts articles into a Supabase database.
- Exposes REST endpoints:

Endpoints:
- GET /articles       : Returns all articles
- POST /articles      : Inserts a new article
- POST /articles/fetch: Fetches latest RSS articles (optional feed URL)

Deployment
----------
- **Render**: Hosts the FastAPI application.
- Environment variables:

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
DATABASE_URL=postgresql://user:pass@host:port/dbname

- Start command on Render:
uvicorn main:app --host 0.0.0.0 --port $PORT

RSS Import Scheduler
-------------------
- **GitHub Actions** used as a free scheduler.
- Workflow file: .github/workflows/rss-cron.yml
- Triggers:
  - Schedule (cron), e.g., every 6 hours
  - Manual trigger (workflow_dispatch)

- Actions performed:
  1. Fetch top N RSS articles
  2. Insert new articles into Supabase via /articles endpoint
  3. Deduplicate based on URL
  4. Log inserted vs skipped articles as artifacts

- Optional: Send email notifications on success/failure using SMTP secrets

Local Testing
-------------
1. Clone repo:
   git clone https://github.com/your-org/fastapi-supabase-api.git
   cd fastapi-supabase-api

2. Install dependencies:
   pip install -r requirements.txt

3. Run server locally:
   uvicorn main:app --reload

4. Test endpoints:
   # GET articles
   curl -X GET "http://127.0.0.1:8000/articles"

   # POST article
   curl -X POST "http://127.0.0.1:8000/articles" \
        -H "Content-Type: application/json" \
        -d '{"title":"Test","url":"https://example.com"}'

Notes
-----
- **Render** handles HTTP hosting.
- **Supabase Edge Functions** can handle article insertion (articles-insert) and fetching (articles-get-api) if using serverless.
- GitHub Actions scheduler is a free workaround to avoid paid cron jobs on Render.
