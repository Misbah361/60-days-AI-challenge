# Day 13 – Embedding Explorer: Dense Embeddings vs TF-IDF

TF-IDF vectors fail when words differ but the meaning is the same. This project compares my **Day 9 TF-IDF** similarity scores with **dense sentence embeddings** on the same sentences.

## Setup
- 20 sentences, 4 topics (Animals, Aviation, Cooking, Technology), 5 each. The first 10 are my Day 9 sentences; I added 10 new ones.
- TF-IDF: Day 9 code and settings (`TfidfVectorizer(stop_words='english')`).
- Embeddings: `all-MiniLM-L6-v2` (sentence-transformers, 384 dimensions). I used this free open-source model instead of the OpenAI API because I had no API access.

## Results
**Average similarity**

| Pairs | TF-IDF | Embeddings |
|---|---|---|
| Same topic | 0.040 | 0.313 |
| Different topic | 0.000 | 0.028 |

**Five paraphrase pairs (different words, same meaning)**

| Pair | TF-IDF | Embedding |
|---|---|---|
| "Pilots fly the airplane across the ocean" / "Aviators cross the sea in aircraft" | 0.000 | 0.730 |
| "Developers write code to build mobile apps" / "Programmers create software for smartphones" | 0.000 | 0.715 |
| "Bake the bread in a hot oven" / "Loaves are baked inside a very warm stove" | 0.000 | 0.653 |
| "A puppy is a young dog that loves to play" / "Juvenile canines enjoy frolicking and games" | 0.000 | 0.635 |
| "The airplane landed at the airport" / "The jet touched down at the terminal" | 0.000 | 0.570 |

**`embed_and_recommend()`** returns the top 3 semantically similar sentences. For the query "A young dog likes to play" it found the paraphrase "Juvenile canines enjoy frolicking and games" (0.683), which my Day 9 `find_similar()` could not find at all.

**K-means (k=4):** 90% agreement with the original topics (18 of 20 sentences), Adjusted Rand Index 0.756. The two misplaced sentences were technology sentences ("Neural networks learn patterns..." and "The wifi router lost its internet connection"), which were grouped with Aviation. They share no obvious context with the other technology sentences, which are about phones and software.

**Time and cost:** 0.379 s for 20 sentences (about 157 tokens). Actual cost with the local model: $0.00. Estimated cost on OpenAI `text-embedding-3-small`: about $0.000003.

## Sparse TF-IDF vs dense embeddings
TF-IDF gives each sentence a sparse vector with one dimension per word, so it only encodes which words appear and how rare they are. "dog" and "puppy" are completely unrelated to it (Day 9 score: 0.000). Dense embeddings are learned by a neural network from huge amounts of text, so the vector encodes meaning and context. Words and sentences used in similar contexts land close together even with no shared vocabulary, which is why embeddings generalise across wording. TF-IDF is free, fast and good for exact keyword matching, while embeddings are better for semantic search, recommendation and clustering.

## Files
- `Day13_Embedding_Explorer.ipynb` – full notebook with outputs
- `day13_heatmaps.png`, `day13_paraphrase_pairs.png`, `day13_clusters.png`
