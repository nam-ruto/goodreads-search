from elasticsearch import Elasticsearch
 
# Connect to local Elasticsearch (started via docker-compose)
es = Elasticsearch("http://localhost:9200")
 
INDEX_NAME = "books"
 
# Define the index mappings
mappings = {
    "mappings": {
        "properties": {
            "title": {
                "type": "text",           # Full-text searchable
                "fields": {
                    "keyword": {
                        "type": "keyword" # Also stored as keyword for exact match/sorting
                    }
                }
            },
            "author": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "genre": {
                "type": "keyword"         # Exact match only (for filtering)
            },
            "rating": {
                "type": "float"           # Numeric — supports range queries
            },
            "num_ratings": {
                "type": "integer"
            },
            "year_published": {
                "type": "integer"
            },
            "description": {
                "type": "text"            # Full-text searchable
            }
        }
    },
    "settings": {
        "number_of_shards": 1,            # Fine for local dev
        "number_of_replicas": 0           # No replicas needed locally
    }
}
 
def create_index():
    # Delete index if it already exists (clean slate)
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"🗑️  Deleted existing index: '{INDEX_NAME}'")
 
    # Create the index with our mappings
    es.indices.create(index=INDEX_NAME, body=mappings)
    print(f"✅ Created index: '{INDEX_NAME}'")
    print(f"\n📋 Field mappings:")
    for field, config in mappings["mappings"]["properties"].items():
        print(f"   {field:20s} → {config['type']}")
 
if __name__ == "__main__":
    create_index()