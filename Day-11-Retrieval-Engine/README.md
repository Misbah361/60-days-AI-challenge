# Day 11: Mini Retrieval Engine

A small information retrieval system that takes a user query and returns the most relevant documents from a knowledge base, ranked by TF-IDF cosine similarity. If nothing is similar enough, it says so honestly instead of returning a low-quality result.

## Topic
Space and Astronomy, a knowledge base of 22 short documents stored as a Python list.

## Tools
Python, scikit-learn, NumPy, NLTK

## How it works
1. Every document is cleaned with my Day 10 `PreprocessingModule` (tokenise, lowercase, remove stop words, strip punctuation, lemmatise).
2. My Day 10 `VectorizerModule` builds the TF-IDF matrix once. Its shape is 22 documents x 167 terms.
3. `retrieve(query, corpus_matrix, top_k=3)` cleans the query the same way, vectorises it, and computes cosine similarity against every document.
4. Relevance threshold: if the highest similarity score is below 0.1, the function returns "No relevant document found." instead of a weak match.

## Test results (10 queries)
| # | Query | Type | Result |
|---|-------|------|--------|
| 1 | Which planet has rings? | clear | Correct: Saturn |
| 2 | What is a black hole? | clear | Correct |
| 3 | How do rockets reach orbit? | clear | Correct |
| 4 | Tell me about the red planet | clear | Failure: Jupiter ranked above Mars |
| 5 | Chandrayaan Moon landing | clear | Failure: generic Moon documents, ISRO document missed |
| 6 | star | ambiguous | Stars and Sun documents both returned (valid readings) |
| 7 | What is the largest thing? | ambiguous | Only Jupiter returned |
| 8 | How do I bake chocolate cake? | out-of-domain | Correctly rejected by the threshold |
| 9 | Who won the cricket world cup? | out-of-domain | Correctly rejected by the threshold |
| 10 | Which frozen wanderer leaves a luminous trail? | synonym | Failure: no match, although the comet document exists |

## Failure analysis
- **Query 4 (red planet):** Jupiter's document also contains "red" and "planet", so it scores almost the same as Mars, and TF-IDF cannot tell that "red planet" means Mars.
- **Query 5 (Chandrayaan):** The Day 10 preprocessing turns "Chandrayaan-3" into the single token "chandrayaan3", which never matches the query word "chandrayaan".
- **Query 7 (largest thing):** "thing" appears in no document, so "largest" alone decides the result and other large objects (galaxy, universe) are never considered.
- **Query 10 (frozen wanderer):** The query shares no words with the comet document ("icy", "glowing", "tails"), so every score falls below 0.1.

## Key learning: vocabulary mismatch
TF-IDF only matches exact tokens, so it fails whenever a query and a document use different words for the same idea. It cannot know that "frozen" means "icy" or that "luminous" means "glowing". The threshold turns this failure into an honest "not found", but the answer was in the knowledge base all along. Embeddings place words and sentences with similar meanings close together, so they can retrieve the right document without any shared words. This is why modern retrieval systems use embeddings, or combine them with TF-IDF.

## Files
- `Day11_Retrieval_Engine.ipynb`: full code, 10-query test output, and written analysis

## Next steps
Replace TF-IDF with sentence embeddings and compare the failures above.
