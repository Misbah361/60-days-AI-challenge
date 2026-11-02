# Day 15: My First RAG Pipeline

I connected my Day 14 FAISS semantic search to an LLM and measured whether retrieval reduces hallucination.

## What I built
- **Knowledge base:** 20 chunks about a fictional company (Veridia Labs), so the LLM has no training knowledge of them
- **Retrieval:** `all-MiniLM-L6-v2` embeddings (384-dim, float32) in a FAISS `IndexFlatL2`, the same as Day 14
- **Prompt:** a LangChain `PromptTemplate` that separates `CONTEXT` from `QUESTION`, with a system rule to answer only from the context
- **`generate_with_rag(query)`:** retrieves the top 3 chunks, formats them as context and returns a grounded answer
- **`generate_without_rag(query)`:** calls the LLM with only the question
- **LLM:** `Qwen2.5-1.5B-Instruct`, run locally on a Colab T4 GPU (no API key)

## Files
- `Day15_RAG_Pipeline.ipynb`: full code and outputs
- `day15_rag_architecture.png`: architecture diagram with every transformation labelled

## Five-query comparison
The right chunk was retrieved for all 5 queries.

| Query | Without RAG | With RAG |
|---|---|---|
| Basic plan price per month | "10 INR" (invented) | 499 rupees per month (correct) |
| Accuracy of the Zafran-2 model | vague, assumed it was a weather model | error of about 8 percent (correct) |
| Pro plan API requests per day | "10,000" (invented) | 5,000 (correct) |
| When is customer support available | "typically 24/7" (generic guess) | Monday to Friday, 9 am to 6 pm IST (correct) |
| Where is farm data stored, and how long until it is deleted | "servers managed by Microsoft" (invented) | Mumbai region, deleted within 30 days (correct) |

Without retrieval, the model made up specific numbers or gave generic answers. With retrieval, all 5 were grounded in the knowledge base.

## Two traced failures

**1. "What is the refund window for the annual plan?"** (not in the knowledge base)
- Retrieved: chunks 5, 19, 12. Chunk 5 is the refund policy for the Basic and Pro plans.
- Answer: "14 days" (wrong)
- Cause: **generation drift.** The retrieved chunk was the closest one but did not cover the annual plan. The model borrowed the Pro plan's 14 days instead of saying "I don't know", which the prompt told it to do.

**2. "How many staff work in the Anantnag office?"** (office exists in the knowledge base, headcount does not)
- Retrieved: chunks 15, 7, 8. The right chunk (the office) was retrieved, but the closest chunk was weak (L2 = 1.041).
- Answer: "12 staff members" (wrong)
- Cause: **generation drift.** 12 is the company-wide number of engineers. The model mixed two facts and cited a statement that did not support its answer.

**Bonus (false refusal):** "How many employees are not engineers?" retrieved the right chunk (L2 = 0.380) but the model said "I don't know" instead of computing 42 - 12 = 30.

## What I learned
- RAG fixed hallucination on all 5 questions: the model stopped inventing prices, limits and providers.
- But RAG is not a guarantee. In all three problem cases, retrieval found the right neighbourhood and the small 1.5B model was the weak link.
- Fixes to try: a similarity threshold (helps when the best chunk is far away, as in Failure 2, but not in Failure 1), asking the model to quote the sentence it used, a larger model, and better chunking.
