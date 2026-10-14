# Immigrant AI Chatbot

A multilingual chatbot that helps immigrants find clear, sourced answers to everyday questions about the United States, such as green cards, citizenship, healthcare, and learning English. It answers only from official web pages it has indexed, shows where each answer came from, and says so when it doesn't know.

![Chat interface]
<img width="1917" height="937" alt="image" src="https://github.com/user-attachments/assets/b134a908-f130-44de-8420-2c0828807f42" />


## Why I built this

Immigration information is spread across many government pages, written in dense English, and mistakes can have serious consequences. This project explores whether a retrieval-based chatbot can give short, plain-language answers in the user's own language, while staying grounded in official sources instead of guessing.

## Features

- **Answers grounded in official sources.** The bot retrieves relevant text from indexed pages and answers only from that text.
- **Source links under every answer**, so users can check the original page.
- **"I don't know" behavior.** If the retrieved text doesn't cover a question, the bot says so and points to an official source rather than guessing.
- **Language picker** with English, Spanish, Chinese, Arabic, and Hindi. Answers use simple words and short sentences.
- **Streaming responses**, so answers appear as they are generated.
- **Suggested questions** to help first-time users get started.
- **Legal notice** on the page: general information only, not legal advice.
- **Model fallback.** If the main Gemini model is overloaded, a backup model answers instead.

## How it works

```
User (React app)
      |
      |  POST /chat  (question + language, API key header)
      v
FastAPI backend
      |
      |-- 1. Embed the question (Gemini embeddings, 768 dimensions)
      |-- 2. Retrieve the 4 closest text chunks from Qdrant
      |-- 3. Send question + chunks to Gemini with a grounded prompt
      |-- 4. Stream tokens back (server-sent events)
      v
User sees the answer, then source links
```

Indexing works the other way: a web page is loaded, split into 1000-character chunks, embedded, and stored in Qdrant along with its URL.

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | React (Create React App), plain CSS |
| Backend | Python, FastAPI, Uvicorn |
| AI orchestration | LangChain |
| LLM | Google Gemini (`gemini-flash-latest`, fallback `gemini-2.5-flash-lite`) |
| Embeddings | `gemini-embedding-001` (768 dimensions) |
| Vector database | Qdrant (cosine similarity) |

## Project structure

```
.
├── Backend/
│   ├── app.py            # FastAPI app: /chat (streamed) and /indexing
│   ├── index_urls.py     # Script to index a list of web pages
│   └── src/
│       ├── qdrant.py     # Qdrant setup, embeddings, page indexing
│       └── rag.py        # Prompt, retriever, streaming answer logic
└── frontend/
    └── src/
        ├── App.js
        ├── Chat.js       # Chat UI, language picker, sources, suggestions
        └── App.css
```

## Getting started

### Prerequisites

- Python 3.10 or newer
- Node.js and npm
- A [Qdrant](https://qdrant.tech) cluster (the free tier works) and its API key and URL
- A Google AI Studio API key for Gemini

### 1. Clone the repo

```bash
git clone https://github.com/nc-4-8/immigrant-ai-chatbot.git
cd immigrant-ai-chatbot
```

### 2. Backend setup

```bash
cd Backend
```

Install the dependencies. If you use Poetry, run `poetry install`. Otherwise:

```bash
pip install fastapi uvicorn langchain-qdrant langchain-google-genai langchain-community langchain-text-splitters qdrant-client python-decouple beautifulsoup4
```

Create `Backend/.env`:

```
QDRANT_API_KEY=your-qdrant-key
QDRANT_URL=your-qdrant-cluster-url
QDRANT_COLLECTION_NAME=rag_chatbot
GOOGLE_API_KEY=your-google-key
APP_API_KEY=any-long-random-string
USER_AGENT=immigrant-ai-chatbot
```

`APP_API_KEY` is a password you make up. To generate one:

```bash
python -c "import secrets; print(secrets.token_hex(16))"
```

Start the server:

```bash
python -m uvicorn app:app --reload --port 8000
```

The interactive API docs are at `http://localhost:8000/docs`.

### 3. Index some pages

Edit the `urls` list in `Backend/index_urls.py` with official pages you want the bot to use, then run:

```bash
python index_urls.py
```

You can also index one page at a time through `POST /indexing` in the `/docs` page. Running the same URL twice adds duplicate chunks, so only list new pages each time.

### 4. Frontend setup

In a second terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env` with the **same** value as `APP_API_KEY`:

```
REACT_APP_API_KEY=the-same-string-as-APP_API_KEY
```

Start the app:

```bash
npm start
```

Open `http://localhost:3000`.

## API

| Endpoint | Description |
|---|---|
| `POST /chat` | Takes `{ "message": "...", "language": "English" }` and streams the answer as server-sent events (`token`, `done`, and `error` events). |
| `POST /indexing` | Takes `{ "url": "https://..." }` and adds that page to the vector database. |

Both endpoints require an `X-API-Key` header matching `APP_API_KEY`.


## Roadmap

- [ ] Build an evaluation set (50+ questions with known answers) and report accuracy
- [ ] Compare chunk sizes, number of retrieved chunks, and embedding models
- [ ] Add conversation memory
- [ ] Index more official sources and store page dates for freshness
- [ ] Move authentication off the frontend, add rate limiting
- [ ] Translate the interface and add right-to-left layout for Arabic
- [ ] Deploy backend and frontend with a public demo link
- [ ] Add automated tests

## Disclaimer

This project is for general information only and is not legal advice. Immigration rules change often. Always check official government sources and consult a qualified professional about your situation.

## Author

Built by Nihal.
