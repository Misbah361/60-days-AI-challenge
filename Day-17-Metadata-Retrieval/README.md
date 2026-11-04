# Day 17 - Advanced Retrieval with Metadata

Upgrade of the Day 15 RAG pipeline: every document now carries metadata (`source`, `category`, `date`, `document_type`), and retrieval can be constrained with a filter dictionary through `filtered_retrieve(query, filters)`.

**Why:** pure vector similarity is context-blind. It cannot tell a 2021 policy from a 2024 one, or a technical reference from a marketing blurb, because their embeddings look alike.

## Stack
Python, LangChain, FAISS, `all-MiniLM-L6-v2` (local embeddings, no OpenAI key), Google Colab.

## What I built
- A 22-document knowledge base (fictional Veridia Labs) with metadata on every document. It includes outdated versions, marketing blurbs, one doc with a missing date and one doc that belongs to two categories.
- Vectors stored together with their metadata using `FAISS.from_documents`.
- `filtered_retrieve(query, filters)` with three filters: `category`, `document_type` and `min_date` (date cutoff). It searches all vectors and keeps only those that pass the filter, so the top-k always obeys the constraints.
- A five-query comparison with and without filters.

## Results (five queries, top 3)

| Metric | No filter | With filters |
|---|---|---|
| Mean P@1 (correct document ranked first) | 0.6 | 1.0 |
| Mean noise (outdated or marketing chunks) | 1.6 | 0.0 |
| Mean precision (useful results / results returned) | 0.47 | 1.0 |

- Without filters, the refund query ranked the 2021 policy first, and the encryption query ranked the 2020 AES-128 doc first.
- A category filter or a date filter alone was not enough. The combination of category, document type and date cutoff removed the noise.
- Caveat: the filters were chosen knowing the right answer's category and type. A real system would need to infer filters from the query.

## Architecture changes vs Day 15
See `day17_architecture.png`. New components (in green):
1. Metadata attached to each document at indexing time.
2. FAISS index and docstore keep each vector paired with its full metadata.
3. A filters dictionary passed in at query time.
4. `filtered_retrieve()` replaces the plain similarity search before the prompt and LLM steps.

## Limitations (still not handled)
1. **Missing metadata:** doc 20 has no date. It ranked first for "How long do refunds take to arrive?" without a filter, then disappeared once the date filter was on, with no error.
2. **Conflicting / multi-category docs:** doc 21 (card details are tokenised) is both billing and security. Under `category=pricing` it was invisible and only appeared under `category=security`.

## Files
- `Day17_Metadata_Retrieval_FINAL.ipynb` - notebook with outputs
- `day17_architecture.png` - updated architecture diagram
