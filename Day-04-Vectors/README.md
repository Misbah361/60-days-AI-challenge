# Day 4: Vectors - Teaching Meaning to Machines

## Task
Turn sentences into vectors (embeddings) using `sentence-transformers`, then compare them with cosine similarity to see which sentences the model thinks mean the same thing.

## What I Did
1. Installed `sentence-transformers` in Google Colab
2. Loaded the pre-trained model `all-MiniLM-L6-v2`
3. Generated embeddings for 5 sentences (shape: 5 x 384)
4. Compared every pair using cosine similarity and cosine distance

## Sentences Used
| # | Sentence |
|---|----------|
| 0 | The cat is sleeping on the sofa. |
| 1 | A kitten is napping on the couch. |
| 2 | I love playing cricket on weekends. |
| 3 | Machine learning models learn from data. |
| 4 | AI systems are trained using datasets. |

## Results
| Pair | Cosine Similarity |
|------|------------------|
| 0 & 1 (cat / kitten) | 0.727 |
| 3 & 4 (ML / AI) | 0.630 |
| 0 & 2 (cat / cricket) | -0.008 |

Cosine distance for 0 & 1: **0.273**

## Reflection
The similar pairs scored highest even though they share almost no words. The model understood that "cat" is like "kitten" and "sofa" is like "couch", which bag-of-words could never do. I was also surprised that cosine similarity can be slightly negative, and that the cat pair scored higher than the ML pair even though both pairs mean the same thing.

## Key Takeaway
Embeddings capture meaning, not just word counts. They power semantic search, recommendation systems, and RAG.

## Files
- `Day4_Vectors.ipynb`: Colab notebook with all code, outputs, and reflection
