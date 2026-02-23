# Steam Review Summarizer

AI-powered tool that distills hundreds of Steam user reviews into concise bullet points — what players praise and what they criticize.

**[Live Demo](https://steam-review-summarizer.vercel.app/)**

---

## How It Works

1. Search for any game on Steam using the autocomplete dropdown
2. The backend fetches up to 100 recent reviews from Steam's API
3. Reviews are cleaned, filtered to opinion sentences, and encoded into semantic vectors using a neural embedding model
4. K-Means clustering groups sentences by topic
5. TF-IDF identifies the distinctive keywords for each cluster
6. An LLM (via OpenRouter) generates a short phrase summarizing each cluster — all clusters are processed in parallel
7. Vague or sentiment-mismatched outputs are filtered before the results are returned

---

## Tech Stack

**Frontend**
- React 18 + Vite
- Plain CSS with Steam-inspired dark theme
- Deployed on Vercel

**Backend**
- FastAPI (Python)
- fastembed — neural sentence embeddings via ONNX Runtime
- scikit-learn — K-Means clustering + TF-IDF
- OpenRouter API — LLM summary generation
- Docker — containerized for consistent deployment
- Deployed on Render

---

## Local Setup

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```
OPENROUTER_API_KEY=your_key_here
```

```bash
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

---

## API

| Endpoint | Method | Params | Description |
|---|---|---|---|
| `/search` | GET | `q` (string) | Autocomplete — returns list of `{appid, name}` |
| `/summarize` | GET | `app_id` (string) | Returns `{game, app_id, summary: {praised, criticized}}` |
| `/` | GET/HEAD | — | Health check |

---

## Project Structure

```
steam-review-summarizer/
├── backend/
│   ├── app/
│   │   ├── main.py          # Routes + CORS
│   │   ├── steam_scraper.py # Steam API calls
│   │   ├── analysis.py      # Embeddings, clustering, TF-IDF
│   │   ├── generator.py     # LLM prompting + output filters
│   │   └── summarizer.py    # Pipeline orchestrator
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx
        └── components/
            ├── SearchBar.jsx
            ├── LoadingSpinner.jsx
            └── ResultDisplay.jsx
```
