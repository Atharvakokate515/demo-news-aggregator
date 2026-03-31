# 🤖 AI News Aggregator

An automated pipeline that scrapes AI news from YouTube, OpenAI, and Anthropic, generates summaries using LLMs, ranks them by relevance to your profile, and delivers a personalized daily email digest.

---

## How It Works

The pipeline runs in 5 stages:

```
1. Scrape  →  2. Enrich  →  3. Digest  →  4. Rank  →  5. Email
```

1. **Scrape** — Fetches latest YouTube videos, OpenAI blog posts, and Anthropic articles via RSS feeds
2. **Enrich** — Fetches YouTube transcripts and converts Anthropic articles to Markdown
3. **Digest** — Uses an LLM agent to generate a concise title + 2–3 sentence summary per article
4. **Rank** — A curator agent scores each digest by relevance to your user profile (0–10)
5. **Email** — Sends a personalized HTML email with the top N articles

---

### FlowChart
```mermaid
flowchart LR

YT[YouTube] --> SC[Scrape]
OA[OpenAI] --> SC
AN[Anthropic] --> SC

SC --> DB[(Database)]
DB --> EN[Enrich]
EN --> DI[Digest]
DI --> RA[Rank]
RA --> EM[Email]
```
---

## Project Structure

```
ai-news-aggregator/
├── main.py                         # Entry point
├── app/
│   ├── config.py                   # YouTube channel IDs
│   ├── runner.py                   # Runs all scrapers
│   ├── daily_runner.py             # Orchestrates the full pipeline
│   ├── profiles/
│   │   └── user_profile.py         # Your interests & preferences
│   ├── scrapers/
│   │   ├── youtube.py              # YouTube RSS + transcript fetcher
│   │   ├── openai.py               # OpenAI RSS scraper
│   │   └── anthropic.py            # Anthropic RSS + Markdown converter
│   ├── agent/
│   │   ├── digest_agent.py         # Generates article summaries
│   │   ├── curator_agent.py        # Ranks articles by relevance
│   │   └── email_agent.py          # Writes personalized email intro
│   ├── services/
│   │   ├── process_youtube.py      # Fills in missing transcripts
│   │   ├── process_anthropic.py    # Fills in missing Markdown
│   │   ├── process_digest.py       # Runs digest generation
│   │   ├── process_curator.py      # Runs ranking
│   │   └── process_email.py        # Builds and sends the email
│   ├── database/
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   ├── connection.py           # DB connection / session
│   │   ├── repository.py           # All DB read/write operations
│   │   └── create_tables.py        # Creates tables on first run
│   └── services/
│       └── email.py                # SMTP email sender + HTML renderer
├── docker/
│   └── docker-compose.yml          # Postgres + app services
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/ai-news-aggregator.git
cd ai-news-aggregator
```

### 2. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp app/example.env .env
```

```env
HUGGINGFACE_API_TOKEN=hf_...

# For cloud deployment (Render, Railway, etc.)
DATABASE_URL=postgresql://user:password@host/db

# For local development
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ai_news_aggregator
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Gmail credentials
MY_EMAIL=you@gmail.com
APP_PASSWORD=xxxx xxxx xxxx xxxx

# Optional: proxy for YouTube transcript API
PROXY_USERNAME=
PROXY_PASSWORD=
```

### 3. Start the database

```bash
cd docker && docker-compose up -d postgres
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the pipeline

```bash
python main.py 24 10
# args: <hours_back> <top_n_articles>
```

This will automatically create the database tables on first run, then execute the full pipeline.

---

## Customizing Your Profile

Edit `app/profiles/user_profile.py` to match your interests. The curator agent uses this to score and rank articles:

```python
USER_PROFILE = {
    "name": "Your Name",
    "background": "...",
    "interests": [
        "Large Language Models",
        "RAG systems",
        # add your own
    ],
    "preferences": {
        "prefer_technical_depth": True,
        "avoid_marketing_hype": True,
    },
    "expertise_level": "Advanced"
}
```

---

## Adding YouTube Channels

Edit `app/config.py` to add or remove channels by their YouTube channel ID:

```python
YOUTUBE_CHANNELS = [
    "UCawZsQWqfGSbCI5yjkdVkTA",  # Matthew Berman
    "UCn8ujwUInbJkBhffxqAPBVQ",  # Dave Ebbelaar
]
```

---

## Running with Docker

To run the full pipeline (app + database) in containers:

```bash
cd docker && docker-compose up
```

Override the default hours/articles via environment variables:

```bash
HOURS_BACK=48 TOP_N=15 docker-compose up
```

---

## Database Models

| Table | Purpose |
|---|---|
| `youtube_videos` | Video metadata + transcripts |
| `openai_articles` | OpenAI RSS articles |
| `anthropic_articles` | Anthropic articles + Markdown |
| `digests` | LLM-generated summaries (one per article) |

---

## Tech Stack

| Component | Technology |
|---|---|
| Scraping | `feedparser`, `youtube-transcript-api`, `docling` |
| LLM Agents | `langchain`, `HuggingFace` (Llama 3 8B) |
| Database | PostgreSQL + SQLAlchemy |
| Email | Python `smtplib` + MIME + `markdown` |
| Containerization | Docker + Docker Compose |

---
