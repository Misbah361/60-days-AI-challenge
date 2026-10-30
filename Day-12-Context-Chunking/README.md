# Day 12 - Context Chunking Experiment

Compares chunking strategies on one long document (Wikipedia: *Machine learning*, 60,195 characters, about 20 pages) to see how chunk design affects retrieval quality.

**Tools:** Python, LangChain (`RecursiveCharacterTextSplitter`), scikit-learn (TF-IDF retrieval)

## What the notebook does
1. Loads the article as one plain string
2. Manual fixed-size chunking with a loop (no LangChain)
3. LangChain recursive character splitting
4. 12 configurations: chunk sizes 100 / 300 / 500 / 1000 x overlaps 0 / 50 / 100
5. Runs the same query on every configuration: *"What is overfitting and how can it be reduced?"*
6. Scores each configuration by how much of the answer passage its best chunk contains
7. Documents three sentences split mid-thought, with exact character positions
8. Recommends a chunk size and overlap

## Results
| chunk_size | top-1 chunk | answer in chunk | precision |
|---|---|---|---|
| 100 | heading only `=== Overfitting ===` | 0% | 0% |
| 300 | heading only `=== Overfitting ===` | 0% | 0% |
| 500 | full answer, 340 chars | 100% | about 87% |
| 1000 | full answer plus unrelated section, 916 chars | 100% | about 32% |

The 100 and 300 character configurations score a similarity of 1.000 because the heading chunk contains the query word, but the chunk holds none of the answer.

## Mid-word cuts (size 300 / 500 / 1000, overlap 50)
Manual fixed-size chunking cuts through a word in 63.5% / 73.9% / 60.9% of chunks. LangChain's recursive splitter cuts through a word in 0% of chunks.

## Three boundary failures (fixed-size chunking, size 300, overlap 0)
| # | Split position | Chunk ends | Next chunk starts |
|---|---|---|---|
| 1 | 300 | `...optimisation method` | `s compose the foundations...` |
| 2 | 20100 | `...The backpropagated valu` | `e (secondary reinforcement)...` |
| 3 | 39900 | `...within the machine learn` | `ing domain typically leverage...` |

All three cut through a word. Overlap of 50-100 characters puts these sentences whole into at least one chunk.

## Recommendation
Use `RecursiveCharacterTextSplitter` with `chunk_size=500` and `chunk_overlap=50`. All three 500-character configurations tie on retrieval (full answer, 87% precision); overlap 50 is chosen because it protects sentences at chunk boundaries at a small cost in extra chunks. It returns the complete answer with the least irrelevant text. Smaller chunks lose the answer, larger chunks add noise, and recursive splitting breaks at paragraph and sentence boundaries instead of mid-word.

## Run it
Open `Day12_Context_Chunking.ipynb` in Google Colab and choose Runtime > Run all.
