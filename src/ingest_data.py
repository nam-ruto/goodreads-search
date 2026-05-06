import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

INDEX_NAME = "books"

# Connect to local Elasticsearch
es = Elasticsearch("http://localhost:9200")


def _publication_year(value) -> int:
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return 0
    return int(ts.year)


def load_csv(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    print(f"📂 Loaded {len(df)} books from CSV")
    print(f"   Columns: {list(df.columns)}\n")
    return df


def df_to_actions(df: pd.DataFrame):
    """
    Generator that yields one Elasticsearch action dict per row.
    The bulk() helper consumes this generator and batches the requests.
    """
    for _, row in df.iterrows():
        yield {
            "_index": INDEX_NAME,
            "_id": int(row["bookID"]),
            "_source": {
                "title": row["title"],
                "author": row["authors"],
                "genre": "",
                "rating": float(row["average_rating"]),
                "num_ratings": int(row["ratings_count"]),
                "year_published": _publication_year(row["publication_date"]),
                "description": "",
            },
        }


def ingest(filepath: str):
    df = load_csv(filepath)

    print("⏳ Indexing documents...")
    success_count, errors = bulk(es, df_to_actions(df))

    print(f"✅ Indexed {success_count} documents successfully")
    if errors:
        print(f"⚠️  {len(errors)} errors occurred:")
        for err in errors:
            print(f"   {err}")

    # Refresh so documents are immediately searchable
    es.indices.refresh(index=INDEX_NAME)
    print(f"\n🔍 Index is ready to search!")


if __name__ == "__main__":
    ingest("data/books.csv")
