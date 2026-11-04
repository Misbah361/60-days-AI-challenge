# Day 18: Hallucination Understanding and Detection

Hallucination is not a random bug. It is a predictable result of how language models generate text: they predict the next most likely token instead of retrieving verified facts. In this experiment I measured how often an LLM fabricates information, compared it with a RAG pipeline, and built a four-signal hallucination detector.

## Setup
- **Generator:** Qwen2.5-1.5B-Instruct (local, run on a Colab T4 GPU) in place of GPT-4o-mini, because I do not have an OpenAI API key
- **Embeddings:** all-MiniLM-L6-v2
- **Retrieval:** FAISS flat index (the Day 15 RAG pipeline, top-3 chunks)
- **Knowledge base:** 30 documents (20 ground-truth fact documents plus 10 distractors)
- **Dataset:** 20 factual questions across 5 groups: Science, History, Geography, Technology and Obscure (rare facts), each with a known ground-truth answer

## Scoring criteria (defined before scoring)
| Label | Criteria |
|---|---|
| Correct | The main fact matches the ground truth in meaning |
| Partially correct | The main fact is right but a supporting detail is wrong or missing |
| Hallucinated | The main fact is wrong, or the model invents names, numbers or dates |

Hallucination types: fabricated specific fact, outdated info presented as current, confident wrong answer, plausible but unverifiable claim.

## Results
| Condition | Correct | Hallucinated | Hallucination rate |
|---|---|---|---|
| No context | 13 | 7 | **35%** |
| With RAG | 20 | 0 | **0%** |

RAG reduced the hallucination rate by 35 percentage points.

**By domain (no-context failures):** Science 1/4, History 0/4, Geography 0/4, Technology 2/4, Obscure 4/4. Common facts (gold, Berlin Wall, Canberra) were answered correctly without context. Rare facts were where the model failed.

## Categorised failure table (no-context condition)
| ID | Domain | Question | Model said | Truth | Type |
|---|---|---|---|---|---|
| 4 | Science | Planet with most known moons | Jupiter (79 moons) | Saturn | Outdated info as current |
| 15 | Technology | What does FAISS stand for | "Facebook AI Research System" | Facebook AI Similarity Search | Fabricated specific fact |
| 16 | Technology | Encoder layers in base Transformer | Three | 6 | Confident wrong answer |
| 17 | Obscure | 1962 Nobel Prize in Physics | "Ralph A. Cahn and Walter Kohn" | Lev Landau | Fabricated specific fact |
| 18 | Obscure | Atomic number of Hassium | 109 | 108 | Confident wrong answer |
| 19 | Obscure | University of Kashmir established | 1973 | 1948 | Confident wrong answer |
| 20 | Obscure | Authors of "Distilling the Knowledge..." | Goodfellow, Bengio, Courville | Hinton, Vinyals, Dean | Confident wrong answer |

Summary: 4 confident wrong answers, 2 fabricated specific facts, 1 outdated-info case. No "plausible but unverifiable" cases appeared, because every question had a checkable answer. The model never hedged on any wrong answer.

## A RAG issue I found and fixed: citation accuracy
In the first RAG run, all 20 answers were correct, but only **5 of 20** cited the right source document. My prompt contained the example "[doc3]" and the small model copied it into most answers. After changing the prompt to "cite the id of the context chunk you used", citation accuracy rose to **20 of 20**. Lesson: small models copy examples in prompts.

## Four-signal hallucination detector
Each signal returns a flag (1 means suspicious):
1. **Unsupported claim detection:** numbers, dates and named entities in the response that do not appear in the retrieved context
2. **Retrieval overlap check:** Jaccard similarity between response tokens and retrieved chunk tokens, flagged if below 0.15
3. **Contradiction detection:** a second LLM call asking "Does this response contradict the provided context? Answer yes or no."
4. **Citation absence check:** factual assertions with no reference to a source document

Final confidence score = 1 - (flags / 4). A response with confidence of 0.5 or lower is predicted to be a hallucination. The notebook prints a per-response breakdown for every answer.

**Detector performance on no-context answers:** TP=6, FP=8, FN=1, TN=5, giving precision 0.43 and recall 0.86. On the RAG answers there were no hallucinations, so precision and recall are undefined.

**Findings per signal:**
- **Signal 1 was the most useful.** It fired on 6 of 7 hallucinations, but also on 8 of 13 correct answers, because correct answers often add true details (dates, names) that are not in the retrieved chunk.
- **Signal 4 fires on every no-context answer by design,** since those answers contain no citations. Together with signal 1 it caused all 8 false positives.
- **Signal 2 was weak.** It caught only 2 of 7 hallucinations.
- **Signal 3 never fired** (0 of 40 answers), not even on Hassium = 109 against a context that says 108. A 1.5B model is too weak to act as a contradiction judge.
- **One hallucination was missed** ("three encoder layers"). It had no number or named entity that signal 1 could check.

## Key takeaways
- Hallucination concentrates on rare facts. Common facts were answered correctly even without context.
- RAG took the hallucination rate from 35% to 0%, but this is a best case because the knowledge base contains the answers.
- Retrieval fixes facts, but citations need checking too. The model's citations were wrong until the prompt was fixed.
- Rule-based signals catch many hallucinations but produce false alarms. A small model cannot replace a strong judge for the contradiction check.

## Limitations
- Only 20 questions, so the rates are rough estimates
- The knowledge base was built from the same ground truth as the questions, so RAG is shown at its best
- A 1.5B model was used instead of GPT-4o-mini, so hallucination rates would likely be lower with a larger model
- Labels were checked manually against ground truth, with a keyword check suggesting the first label

## Files
- `Day18_Hallucination_Detection.ipynb`: full notebook with outputs
- `results.json`: all 40 recorded responses (20 no-context, 20 RAG)
- `detector_breakdown.csv`: per-response detector signals and confidence scores
- `day18_hallucination_rates.png`: hallucination rate chart

## How to run
Open the notebook in Google Colab with a T4 GPU runtime and run all cells from the top. No API key is needed.
