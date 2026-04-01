# Hockey RAG Assistant

A Retrieval-Augmented Generation (RAG) application for querying real-time NHL hockey data using natural language. Built with Python, ChromaDB, sentence-transformers, Claude API, and Streamlit.

## Screenshots

**Team Performance and Standings**
![Devils Performance](screenshots/devils_performance.png)

**Player Season Stats**
![Jack Hughes Points](screenshots/jack_hughes_points.png)

**Post Olympic Break Analysis**
![Jack Hughes Olympic Break](screenshots/jack_hughes_olympics.png)

**Top Scorers**
![Carolina Top Scorers](screenshots/carolina_top_scorers.png)

## Overview

This application demonstrates a production-style RAG pipeline applied to a real-world domain. It ingests live NHL data from multiple sources, processes it into semantically meaningful document chunks, embeds and stores them in a vector database, and uses Claude to generate grounded natural language answers.

The project addresses a genuine gap in the sports analytics market. Tools like Natural Stat Trick, MoneyPuck, and Hockey Reference provide rich NHL data through dashboards and tables. None provide a natural language interface that lets fans and analysts ask complex questions in plain English and receive grounded, data-backed answers. The dream state of this application would compile data from every possible source: betting odds, game logs, news articles, even practice logs, to allow fans and employees of the NHL and their teams to query data and get close to real-time responses back. Whether you're just a fan playing fantasy hockey, a sports bettor, or an NHL scout looking for data on trades, RAG in its final form with all that data could unlock a lot of value.

**Supported teams:** New Jersey Devils, Carolina Hurricanes, New York Islanders

## Example Questions

- "How are the New Jersey Devils performing this season?"
- "Who are the top scorers on the Carolina Hurricanes?"
- "How many points does Jack Hughes have?"
- "How has Jack Hughes been playing since the Olympic break?"
- "What are Nico Hischier's last 10 games like?"
- "How is Sebastian Aho performing this season?"

## Architecture
```
Data Sources → Ingestion → Processing → Vector Store → Retrieval → Generation → UI
```

### Data Sources
- **NHL API** — Live standings, rosters, team stats, and player game logs
- **ESPN RSS** — Recent NHL news and analysis
- **Sportsnet RSS** — Additional NHL coverage

### Document Processing

Raw data is transformed into semantically rich text documents across several types:

- **Standings documents** — Current team records and division and conference rankings
- **Player stats documents** — Individual season statistics per player
- **Scoring summaries** — Pre-ranked top scorers per team
- **Season summary documents** — Aggregated season stats per key player
- **Post Olympic break summaries** — Performance stats since February 25 2026
- **Last 10 game summaries** — Recent form with game by game breakdown
- **Individual game log entries** — Single game performance records

### Retrieval Strategy

Pure semantic search struggles with ranked and time-filtered queries. This application uses intent detection to route queries to the appropriate document type before falling back to semantic search.

| Intent | Trigger Phrases | Document Type |
|--------|----------------|---------------|
| Team performance | "how are the", "standings", "playoff" | standings |
| Top scorers | "top scorers", "leading scorer" | scoring_summary |
| Season stats | "how many points", "this season" | season_summary |
| Olympic break | "olympic break", "since olympics" | post_olympic_summary |
| Last 10 games | "last 10", "recent form" | last_10_games |
| General | everything else | semantic search |

### Key Design Decisions

**Pre-ranked scoring summaries** — Semantic search cannot sort by points. Creating explicit ranked documents at processing time solves this cleanly without requiring a reranking model.

**Intent-aware retrieval over pure semantic search** — For structured data questions, keyword-based intent routing to filtered document types significantly outperforms embedding similarity alone.

**Sentence-transformers for embeddings** — Uses all-MiniLM-L6-v2 locally, avoiding OpenAI embedding API costs while maintaining strong retrieval quality.

**Direct component integration over LangChain abstractions** — Built the RAG pipeline using core components directly including sentence-transformers, ChromaDB Python client, and Anthropic SDK rather than relying on LangChain wrappers. This approach provides deeper understanding of each layer and more control over retrieval behavior.

**Known limitations** — News articles provide summaries only due to RSS free tier constraints. Post Olympic break comparisons between players require both players summaries to surface in the same retrieval window.

## Tech Stack

- **Python 3.11**
- **ChromaDB** — Local vector database
- **sentence-transformers** — Local embeddings using all-MiniLM-L6-v2
- **Anthropic Claude API** — Response generation
- **Streamlit** — Conversational UI
- **feedparser** — RSS ingestion
- **NHL API** — Live hockey data

## Setup

### Prerequisites
- Python 3.11+
- Anthropic API key

### Installation
```bash
git clone https://github.com/ehale06/hockey-rag
cd hockey-rag
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Create a .env file:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Run
```bash
# Step 1 — Ingest data from NHL API and RSS feeds
python src/ingest.py

# Step 2 — Process raw data into document chunks
python src/process.py

# Step 3 — Build vector store
python src/retrieval.py

# Step 4 — Launch the app
streamlit run src/app.py
```

## Project Structure
```
hockey-rag/
├── src/
│   ├── ingest.py        # Data ingestion from NHL API and RSS
│   ├── process.py       # Document processing and chunking
│   ├── retrieval.py     # Vector store and intent-aware retrieval
│   ├── rag_chain.py     # Claude integration and RAG chain
│   └── app.py           # Streamlit UI
├── screenshots/         # Application screenshots
├── data/                # Raw and processed data (gitignored)
├── .chroma/             # ChromaDB vector store (gitignored)
├── .env.example         # Environment variable template
├── requirements.txt     # Dependencies
└── README.md
```

## Data Refresh

Re-run the pipeline to fetch fresh data:
```bash
python src/ingest.py
python src/process.py
python src/retrieval.py
```
