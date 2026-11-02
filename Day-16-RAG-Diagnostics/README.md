# Day 16: RAG Diagnostics and Debugging

I took my Day 15 RAG pipeline (MiniLM + FAISS + LangChain prompt + local Qwen2.5-1.5B) and diagnosed where and why it fails, then fixed what I could and measured the effect.

## What I built
- **15-query test suite** targeting five failure modes (3 queries each)
- **Automatic logging:** every pipeline call writes the retrieved chunks, distances, truncation info and the answer to `rag_results.json`
- **Failure classification table** with a one-sentence cause per query
- **Tracing** of failures back to a chunking or embedding decision
- **Three fixes**, measured one after another: chunk overlap, similarity threshold, refined prompt
- **Scorecard:** retrieval quality (1-5) and answer quality (1-5) per query, averaged

## Files
- `Day16_RAG_Diagnostics.ipynb`: code and outputs
- `rag_results.json`: log of every call
- `failure_table.csv`, `failure_classification_baseline.csv`, `scorecard_summary.csv`
- `day16_scorecard.png`: scores after each fix

## Baseline result: 7 passed, 8 failed (plus 1 hidden failure found by hand)

| ID | Targeted mode | Diagnosis | One-sentence cause |
|---|---|---|---|
| Q01 | Retrieval failure | PASS | Both halves of the CTO sentence landed in the top 3 chunks, so the chunk cut did no harm. |
| Q02 | Retrieval failure | PASS | Chunks 6 and 7 were both retrieved, recovering the support hours despite the split. |
| Q03 | Retrieval failure | Retrieval failure | "Urdu, Kashmiri \| and English" was cut between chunks 8 and 9, and chunk 9 ranked #4, so English was dropped. |
| Q04 | Context overflow | Context window overflow | All facts were retrieved, but the 100-word budget cut chunks [3, 5, 2, 7] and the model invented "999 rupees". |
| Q05 | Context overflow | PASS | The summary facts fit in the context and the answer is correct. |
| Q06 | Context overflow | Retrieval failure | The top 6 chunks skipped chunk 7 (support hours and maintenance), which the chunker had split from chunk 6. |
| Q07 | Answer-context mismatch | Answer-context mismatch | Only Basic/Pro refund windows exist; the model answered "10 months" by mixing in the annual-plan sentence. |
| Q08 | Answer-context mismatch | Answer-context mismatch | It answered "12" (company-wide engineers) for the Anantnag office headcount. |
| Q09 | Answer-context mismatch | Answer-context mismatch (relabelled) | The model gave the referral reward to the referred friend; the document gives it to the farmer who refers. |
| Q10 | Vague context | PASS | Correctly refused (best chunk L2 1.094). |
| Q11 | Vague context | PASS | Correctly refused (best chunk L2 1.629). |
| Q12 | Vague context | PASS | Correctly refused (best chunk L2 1.489). |
| Q13 | Correct chunk, wrong answer | Correct chunk, wrong answer | The context had 42 and 12, but the model said "insufficient information" instead of computing 42 - 12. |
| Q14 | Correct chunk, wrong answer | Correct chunk, wrong answer | It said "1,299 rupees for one year", ignoring the 10-month annual rule (should be 12,990). |
| Q15 | Correct chunk, wrong answer | Correct chunk, wrong answer (relabelled) | It says Pro costs 800, then "301 more"; the automatic check only looked for "800" and missed the error. |

## Two traced failures
1. **Q03 (chunking decision):** with chunk_size=40 and overlap=0, the fact was split across chunks 8 and 9. `trace_chunking()` showed no chunk holds the whole sentence, and the half with "English" ranked #4 (L2 1.716), outside the top 3.
2. **Q06 (chunking and embedding):** the support sentence was split between chunks 6 and 7, and the generic query ranked the flagship product chunk first, so chunk 7 was not in the top 6.

A third finding, from Q04: when the context is truncated, the model fills the gap with invented numbers.

## Fixes and results

| Stage | Avg retrieval | Avg answer | Passes (of 15) |
|---|---|---|---|
| Baseline | 4.40 | 3.20 | 7 |
| + A: chunk overlap 15 | 4.40 | 3.33 | 8 |
| + B: similarity threshold 0.878 | 4.40 | 4.13 | 11 |
| + C: refined prompt | 4.40 | 4.07 | 11 |

- **A (overlap):** fixed Q03, but made Q01 and Q12 worse (longer overlapping chunks use up the context budget).
- **B (threshold):** turned Q07, Q09 and Q12 into correct refusals. It refused 6 of 6 unanswerable queries but also wrongly refused one answerable query (Q13).
- **C (prompt):** changed no diagnoses on this small model.

With Q15 corrected to a failing answer, the baseline answer average is 2.93 instead of 3.20.

## What is still broken
- Q08 still answers "12": its best chunk is close enough to pass any distance threshold.
- Q13 and Q14 are arithmetic failures of the small model.
- Q04 and Q06 need a larger context budget or sentence-aware chunking.

## Limits
The threshold was tuned and tested on the same 15 queries, so its gain is optimistic. Scores come from a written rubric, not human judgement. The LLM is small (1.5B).

## What I learned
- Chunking is a real source of failure: a fixed word window cuts sentences, and fixing that (overlap) has side effects.
- Auto-checks can miss errors: Q15 passed a substring check but was wrong.
- A distance threshold catches questions with no relevant chunk, but not missing details inside a relevant chunk.
