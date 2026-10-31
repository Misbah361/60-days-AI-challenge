# Day 14: Semantic Search with FAISS vs Keyword Search

I built a semantic search engine using a FAISS vector index and compared it against a keyword (word-overlap) baseline on the same 50-document corpus.

## What I built
- **Corpus:** 50 short documents across 5 topics (health, tech, cooking, finance, travel)
- **Embeddings:** `all-MiniLM-L6-v2` (local, free), stored as a NumPy `float32` array of shape (50, 384)
- **Index:** FAISS `IndexFlatL2`, with `index.ntotal = 50` confirming every document was stored
- **`semantic_search(query, top_k)`:** embeds the query and returns the nearest neighbours with distance and cosine score
- **`keyword_search(query, corpus, top_k)`:** word-overlap scoring (stopwords removed)
- **Comparison:** 10 test queries run through both systems side by side

## Files
- `Day14_Semantic_Search.ipynb`: full code and outputs
- `day14_architecture.png`: pipeline diagram

## Results

### Semantic search wins (vocabulary mismatch)
| Query | Keyword | Semantic |
|---|---|---|
| cardiovascular workout benefits | no results | correct doc (cos 0.68) |
| my phone has no reception in the lift | no results | correct doc (cos 0.51) |
| cheap airfare tips | no results | correct doc (cos 0.60) |

The query and document share no words (for example "reception" and "lift" vs "signal" and "elevators"), so keyword search fails. The embedding model matches by meaning.

### Keyword search is more precise
| Query | Keyword | Semantic |
|---|---|---|
| HTTP 404 | 1 result, correct | correct top result, plus unrelated docs (cos about 0.1) |
| TLS 1.3 | 1 result, correct | correct top result, plus unrelated docs (cos about 0.1) |
| Vitamin B12 | 1 result, correct | correct top result, plus unrelated docs (cos about 0.2) |

Both methods found the right top document. Keyword search returned only matching documents. Semantic search always returns `top_k` results, so it added unrelated ones. A similarity threshold would fix this: correct documents scored 0.42 to 0.80 and unrelated ones stayed at or below about 0.25.

### Latency and cost
- Query embedding: 18.4 ms (local model), FAISS search: 0.015 ms
- Keyword search: 0.38 ms
- Actual cost: $0 (local model). OpenAI embeddings would be about $2 per 100M tokens.

## Trade-offs
- **Use semantic search** when users phrase queries in their own words (synonyms, paraphrases).
- **Use keyword search** for exact identifiers such as error codes, version numbers and names.
- **At scale:** a flat index scans every vector. At 1M documents the vectors need about 1.5 GB (384-dim) or 6.1 GB (1536-dim), so large systems use approximate indexes (HNSW, IVF).
- **In production:** use a hybrid of both, with a similarity threshold.

## Note
The task suggests OpenAI's `text-embedding-3-small`. I used a local model, the same one as Day 13. The FAISS code is identical for either model, and only the vector size differs (384 vs 1536).
