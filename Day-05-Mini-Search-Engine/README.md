# Day 5: Build a Mini Search Engine

## Goal
Build a small search engine that finds sentences by **meaning** (semantic search) and compare it with plain **keyword search**.

## What I did
1. Created a dataset of **20 sentences** about space and astronomy.
2. Converted every sentence into a vector (384 numbers) using `all-MiniLM-L6-v2` from `sentence-transformers`.
3. Wrote `semantic_search(query, top_k=3)`, which embeds the query and returns the top 3 most similar sentences using cosine similarity.
4. Wrote `keyword_search(query, top_k=3)`, which counts how many words the query shares with each sentence.
5. Ran both searches on the same 3 queries and compared the results.

## How it works
- Sentences with similar meaning get similar vectors.
- A query is embedded the same way as the sentences.
- The sentences with the highest similarity score to the query are returned.

## Example results

| Query | Semantic search (top 1) | Keyword search (top 1) |
|---|---|---|
| How do spacecraft leave the planet? | Rockets burn fuel to escape Earth's gravity and reach orbit (0.509) | The International Space Station circles the planet... |
| Where did humans first step on another world? | Neil Armstrong was the first human to walk on the Moon (0.386) | Neil Armstrong was the first human to walk on the Moon |
| Dangers of junk floating around Earth | Space debris from old satellites threatens active spacecraft (0.465) | Rockets burn fuel to escape Earth's gravity... |

## Key finding
Keyword search only matches exact words, so it can return wrong results that happen to share a common word like "Earth" or "the". Semantic search matched meaning: it linked "junk" to "debris" and "leave the planet" to "escape Earth's gravity".

## Files
- `Day5_Mini_Search_Engine.ipynb`: notebook with code, example queries, top-3 outputs, and reflection
- `README.md`: this file

## Tools
Python, Google Colab, sentence-transformers, NumPy
