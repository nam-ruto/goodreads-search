from elasticsearch import Elasticsearch
 
es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "books"
 
 
# ─────────────────────────────────────────────
# HELPER: pretty-print search results
# ─────────────────────────────────────────────
def print_results(response, label="Results"):
    hits = response["hits"]["hits"]
    total = response["hits"]["total"]["value"]
    print(f"\n{'='*55}")
    print(f"  {label}  ({total} total hits)")
    print(f"{'='*55}")
    if not hits:
        print("  No results found.")
        return
    for hit in hits:
        src = hit["_source"]
        score = hit.get("_score")
        score_s = f"{score:.2f}" if isinstance(score, (int, float)) else "n/a"
        print(f"  [{score_s}] {src['title']} — {src['author']}")
        print(f"         Genre: {src['genre']} | ⭐ {src['rating']} | {src['year_published']}")
    print()
 
 
# ─────────────────────────────────────────────
# 1. MATCH QUERY — full-text search on one field
#    Elasticsearch tokenizes the text and finds
#    documents that contain matching terms.
# ─────────────────────────────────────────────
def search_by_title(query: str):
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "match": {
                    "title": query   # Analyzed full-text search
                }
            }
        }
    )
    print_results(response, f"match title='{query}'")
 
 
# ─────────────────────────────────────────────
# 2. MULTI_MATCH — search across multiple fields
#    Useful for a general "search everything" bar.
#    Boost (^) makes title matches rank higher.
# ─────────────────────────────────────────────
def search_all_fields(query: str):
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "author^2", "description", "genre"]
                    # ^3 means title matches are 3x more important
                }
            }
        }
    )
    print_results(response, f"multi_match='{query}'")
 
 
# ─────────────────────────────────────────────
# 3. TERM FILTER — exact keyword match
#    Use for structured fields like genre.
#    Does NOT analyze the text (case-sensitive).
# ─────────────────────────────────────────────
def filter_by_genre(genre: str):
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "term": {
                    "genre": genre   # Exact match on keyword field
                }
            }
        }
    )
    print_results(response, f"filter genre='{genre}'")
 
 
# ─────────────────────────────────────────────
# 4. RANGE QUERY — numeric range filtering
#    Works on float/integer fields.
# ─────────────────────────────────────────────
def search_by_rating(min_rating: float, max_rating: float = 5.0):
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "range": {
                    "rating": {
                        "gte": min_rating,  # greater than or equal
                        "lte": max_rating   # less than or equal
                    }
                }
            },
            "sort": [{"rating": {"order": "desc"}}]  # Sort by rating descending
        }
    )
    print_results(response, f"rating between {min_rating} and {max_rating}")
 
 
# ─────────────────────────────────────────────
# 5. BOOL QUERY — combine multiple conditions
#    must     → AND (affects score)
#    filter   → AND (does NOT affect score, faster)
#    should   → OR (boosts score if matched)
#    must_not → NOT
# ─────────────────────────────────────────────
def advanced_search(keyword: str, genre: str = None, min_rating: float = None, max_year: int = None):
    must = [{"multi_match": {"query": keyword, "fields": ["title^2", "description"]}}]
    filters = []
 
    if genre:
        filters.append({"term": {"genre": genre}})
 
    if min_rating:
        filters.append({"range": {"rating": {"gte": min_rating}}})
 
    if max_year:
        filters.append({"range": {"year_published": {"lte": max_year}}})
 
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "bool": {
                    "must": must,
                    "filter": filters     # Filters don't affect relevance score
                }
            }
        }
    )
    label = f"bool search='{keyword}'"
    if genre: label += f" genre='{genre}'"
    if min_rating: label += f" rating>={min_rating}"
    if max_year: label += f" year<={max_year}"
    print_results(response, label)
 
 
# ─────────────────────────────────────────────
# 6. AGGREGATIONS — analytics on your data
#    Like SQL GROUP BY + COUNT/AVG/etc.
# ─────────────────────────────────────────────
def get_aggregations():
    response = es.search(
        index=INDEX_NAME,
        body={
            "size": 0,              # Don't return documents, just aggregations
            "aggs": {
                "books_per_genre": {
                    "terms": {
                        "field": "genre",    # Group by genre
                        "size": 10
                    }
                },
                "avg_rating": {
                    "avg": {"field": "rating"}
                },
                "rating_histogram": {
                    "histogram": {
                        "field": "rating",
                        "interval": 0.5      # Bucket size
                    }
                }
            }
        }
    )
 
    aggs = response["aggregations"]
 
    print(f"\n{'='*55}")
    print("  AGGREGATIONS / ANALYTICS")
    print(f"{'='*55}")
 
    print(f"\n📊 Books per genre:")
    for bucket in aggs["books_per_genre"]["buckets"]:
        print(f"   {bucket['key']:20s} → {bucket['doc_count']} books")
 
    print(f"\n⭐ Average rating across all books: {aggs['avg_rating']['value']:.2f}")
 
    print(f"\n📈 Rating distribution (histogram):")
    for bucket in aggs["rating_histogram"]["buckets"]:
        bar = "█" * bucket["doc_count"]
        print(f"   {bucket['key']:.1f}  {bar} ({bucket['doc_count']})")
 
 
# ─────────────────────────────────────────────
# RUN ALL DEMOS
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🔍 ELASTICSEARCH BOOK SEARCH — DEMO QUERIES\n")
 
    # 1. Simple title search
    search_by_title("hunger games")
 
    # 2. Search across all fields
    search_all_fields("wizard magic journey")
 
    # 3. Filter by exact genre
    filter_by_genre("Dystopian")
 
    # 4. Range: highly rated books
    search_by_rating(min_rating=4.3)
 
    # 5. Bool: combine keyword + filters
    advanced_search(
        keyword="space alien future",
        genre="Science Fiction",
        min_rating=4.0
    )
 
    # 6. Aggregations
    get_aggregations()