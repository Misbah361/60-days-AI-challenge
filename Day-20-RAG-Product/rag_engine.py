"""RAG engine: chunking (Day 12) + FAISS search (Day 14) + metadata filters
(Day 17) + grounding prompt (Day 19), combined into one module."""
import os
import re

import faiss
import torch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from transformers import pipeline

EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.3"))

REFUSAL = "I don't have enough information in my knowledge base to answer that."

GROUNDING_PROMPT = """You are a knowledge assistant for Veridia Labs.
Answer ONLY using the context below. Never use outside knowledge.
Each context item shows [chunk_id | source file | date].

Rules:
1. If the context contains information that answers the question, answer it in one or two sentences.
2. If two items give different values, they are old and new versions. Use the item with the most recent date, and say the older value is outdated.
3. Only if NO context item relates to the question, reply exactly: "{refusal}"

Context:
{context}

Question: {question}
Answer:"""


class RAGEngine:
    def __init__(self, documents, chunk_size=300, chunk_overlap=50):
        self.embedder = SentenceTransformer(EMBED_MODEL)
        self.llm = pipeline("text-generation", model=LLM_MODEL,
                            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                            device_map="auto")
        self._build_index(documents, chunk_size, chunk_overlap)

    # ---- indexing (Day 12 + Day 14) ----
    def _build_index(self, documents, chunk_size, chunk_overlap):
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                  chunk_overlap=chunk_overlap)
        self.chunks = []
        for doc in documents:
            for i, piece in enumerate(splitter.split_text(doc["text"])):
                self.chunks.append({
                    "chunk_id": f'{doc["id"]}-{i}',
                    "title": doc["title"],
                    "category": doc["category"],
                    "document_type": doc["document_type"],
                    "date": doc["date"],
                    "text": piece,
                })
        vectors = self.embedder.encode([c["text"] for c in self.chunks],
                                       normalize_embeddings=True).astype("float32")
        self.index = faiss.IndexFlatIP(vectors.shape[1])  # inner product = cosine
        self.index.add(vectors)

    # ---- retrieval with metadata filters (Day 17) ----
    def retrieve(self, query, top_k=3, category=None, document_type=None, min_date=None):
        q = self.embedder.encode([query], normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q, len(self.chunks))
        results = []
        for score, i in zip(scores[0], idxs[0]):
            c = self.chunks[i]
            if category and c["category"] != category:
                continue
            if document_type and c["document_type"] != document_type:
                continue
            if min_date and (c["date"] is None or c["date"] < min_date):
                continue
            results.append({**c, "score": float(score)})
            if len(results) == top_k:
                break
        return results

    @staticmethod
    def newest_versions_only(hits):
        """policy_2021.pdf and policy_2024.pdf share the base name policy.pdf;
        keep only the newest version of each."""
        base = lambda t: re.sub(r"_(19|20)\d{2}(?=\.)", "", t)
        best = {}
        for h in hits:
            k = base(h["title"])
            if k not in best or (h["date"] or "") > (best[k]["date"] or ""):
                best[k] = h
        return [h for h in hits if best[base(h["title"])] is h]

    # ---- full pipeline ----
    def ask(self, query, top_k=3, **filters):
        hits = self.retrieve(query, top_k=6, **filters)
        hits = self.newest_versions_only(hits)[:top_k]
        top_score = max((h["score"] for h in hits), default=0.0)
        low_conf = top_score < CONFIDENCE_THRESHOLD

        if low_conf:
            answer = REFUSAL  # gate: never let the LLM answer from its own knowledge
        else:
            ordered = sorted(hits, key=lambda h: h["date"] or "", reverse=True)
            context = "\n".join(
                f'[{h["chunk_id"]} | {h["title"]} | {h["date"]}] {h["text"]}'
                for h in ordered)
            prompt = GROUNDING_PROMPT.format(refusal=REFUSAL, context=context, question=query)
            out = self.llm([{"role": "user", "content": prompt}],
                           max_new_tokens=150, do_sample=False)
            answer = out[0]["generated_text"][-1]["content"].strip()
            if not answer.startswith(REFUSAL[:30]):
                cites = ", ".join(f'{h["chunk_id"]} ({h["title"]})' for h in hits)
                answer += f"\n\nSources: {cites}"

        if low_conf:
            answer += ("\n\n⚠️ Low confidence: the best retrieval match was weak "
                       "(score below 0.3), so this answer may not be well-supported.")

        return {
            "answer": answer,
            "sources": [{"chunk_id": h["chunk_id"], "title": h["title"],
                         "score": round(h["score"], 3)} for h in hits],
            "top_score": round(top_score, 3),
            "low_confidence": low_conf,
        }
