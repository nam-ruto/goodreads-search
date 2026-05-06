# Goodreads book search (Elasticsearch)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- Python **3.10+** (tested with 3.13)

## Quick start

1. **Start Elasticsearch and Kibana**

   ```bash
   docker compose up -d
   ```

   - Elasticsearch: [http://localhost:9200](http://localhost:9200)
   - Kibana: [http://localhost:5601](http://localhost:5601)

   Security is disabled for local development (`xpack.security.enabled=false`). Do not expose this stack to the internet.

2. **Python environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create the index** (deletes an existing `books` index if present)

   ```bash
   python src/setup_index.py
   ```

4. **Load data**

   Place your CSV at `data/books.csv` (see [Data](#data) below), then:

   ```bash
   python src/ingest_data.py
   ```

5. **Run the search demos**

   ```bash
   python src/search.py
   ```

## Project layout

| Path | Purpose |
|------|---------|
| `docker-compose.yml` | Elasticsearch 8.13 + Kibana 8.13, port 9200 / 5601 |
| `data/books.csv` | Source dataset (not committed if you use your own export) |
| `src/setup_index.py` | Defines the `books` index mappings |
| `src/ingest_data.py` | Reads CSV and bulk-indexes documents |
| `src/search.py` | Runnable examples of ES queries |

## Data

Ingest expects a CSV with (at least) these columns, as in typical Goodreads exports:

`bookID`, `title`, `authors`, `average_rating`, `ratings_count`, `publication_date`, …

Documents stored in Elasticsearch:

| Field | Source |
|-------|--------|
| `title`, `author`, `rating`, `num_ratings`, `year_published` | Mapped from CSV (`authors` → `author`; year from `publication_date`) |
| `genre`, `description` | Not in this CSV; ingested as empty strings so the index shape matches the demos |

Some rows may contain commas inside unquoted author names; those break strict CSV parsing. If `read_csv` fails, quote the affected author field(s) or use pandas `on_bad_lines="skip"` (you will drop those rows).

## Requirements

- `elasticsearch==8.13.0` — aligned with the Docker image version  
- `pandas==2.2.2` — CSV loading

## Troubleshooting

- **Connection errors**: ensure `docker compose ps` shows Elasticsearch healthy and port 9200 is free.
- **Genre filter returns no hits**: with the default CSV, `genre` is empty; `filter_by_genre("Dystopian")` will not match until you enrich data or change ingest.
- **`_score` is `n/a` in output**: normal for some queries (for example range + sort) when Elasticsearch does not return a numeric score for hits.

## License

Use and modify for your own learning; dataset licensing depends on where you obtained `books.csv`.
