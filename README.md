# Apex Mentor

**Learn with a teacher that remembers.**

Apex Mentor is a private AI learning companion backend. It keeps a structured memory of what you are learning, what you understand, what you forget, and what needs review. It is designed to help ChatGPT act more like a personalized teacher instead of a simple flashcard reviewer.

The first version runs locally, in Deepnote, or in a small VM. It exposes a private API that can later be connected to ChatGPT through an MCP server or ChatGPT app.

## What it does in v0

- Stores learning concepts in SQLite
- Imports Anki-style CSV exports
- Searches concepts by topic, text, tags, and weak areas
- Tracks review attempts, scores, confidence, and mistakes
- Calculates due reviews using a simple spaced-repetition model
- Generates a review context for ChatGPT to teach from
- Protects private endpoints with a bearer token

## One-command start after cloning

```bash
bash scripts/start.sh
```

The script will:

1. Create a Python virtual environment
2. Install dependencies
3. Create `.env` if missing
4. Initialize local data folders
5. Start the API server

Default local URL:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Quick test

After the server starts, open another terminal and run:

```bash
source .venv/bin/activate
python scripts/demo_seed.py
```

Then visit:

```text
http://127.0.0.1:8000/docs
```

## Private access

Apex Mentor uses a bearer token.

The first run creates `.env` with:

```env
APEX_AUTH_TOKEN=change-me
```

Change it to a strong secret before exposing the server through ngrok, Cloudflare Tunnel, Tailscale, or any HTTPS endpoint.

Requests should include:

```text
Authorization: Bearer YOUR_TOKEN
```

## Deepnote setup

In Deepnote:

```bash
git clone https://github.com/AlsayedHoota/Apex-Mentor.git
cd Apex-Mentor
bash scripts/start.sh
```

For a private external URL, expose port `8000` using your chosen tunnel.

## Anki CSV format

Start with Anki CSV export using columns like:

```csv
front,back,tags,deck
```

Import endpoint:

```text
POST /api/import/anki-csv
```

## Roadmap

- MCP protocol server
- ChromaDB/Qdrant semantic vector memory
- ChatGPT app manifest/config
- Better review scheduling
- Topic mastery dashboard
- APKG import support
