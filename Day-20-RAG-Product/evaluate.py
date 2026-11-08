"""Runs the 15 test queries against the running API and scores them.
Start the server first:  uvicorn app:app --port 8000
Then:  python evaluate.py"""
import json

import pandas as pd
import requests

URL = "http://127.0.0.1:8000/ask"
REFUSAL_START = "I don't have enough information"

# (difficulty, question, expected chunk ids, expected facts; "|" = alternatives)
TESTS = [
    ("easy", "How long do I have to ask for a refund?", ["doc1-0"], ["30"]),
    ("easy", "How many days can employees work remotely?", ["doc17-0"], ["3"]),
    ("easy", "What is the API rate limit on the Pro plan?", ["doc12-0"], ["1000"]),
    ("easy", "What encryption does Veridia Vault use for data at rest?", ["doc5-0"], ["AES-256"]),
    ("easy", "How long are deleted customer records kept in backups?", ["doc8-0"], ["90"]),
    ("medium", "When can I reach support by phone?", ["doc9-0"], ["24/7"]),
    ("medium", "What happens if I exceed the API rate limit?", ["doc12-0"], ["429"]),
    ("medium", "How long does it take for a refund to reach my card?", ["doc20-0"], ["5 business|five business"]),
    ("medium", "Which release added single sign-on?", ["doc15-0"], ["4.2|SAML"]),
    ("medium", "Are my card details stored on Veridia's servers?", ["doc21-0"], ["tokeni|never stored|not stored"]),
    ("hard", "How much does the Pro plan cost?", ["doc3-0"], ["49"]),
    ("hard", "What TLS version is used for data in transit?", ["doc5-0"], ["1.3"]),
    ("hard", "Do annual plans get refunded differently from monthly plans?", ["doc1-0"], ["pro-rata|pro rata|prorata"]),
    ("hard", "What is the annual revenue of Veridia Labs?", [], []),   # out of scope
    ("hard", "What is the boiling point of water?", [], []),            # out of scope
]

rows = []
for difficulty, question, expected_ids, facts in TESTS:
    r = requests.post(URL, json={"query": question}).json()
    answer = r["answer"].split("\n\nSources:")[0].split("\n\n⚠️")[0].strip()
    retrieved = [s["chunk_id"] for s in r["sources"]]
    refused = answer.startswith(REFUSAL_START)

    if expected_ids:  # in-scope: score rank of the right chunk, then the facts
        ranks = [retrieved.index(c) + 1 for c in expected_ids if c in retrieved]
        retrieval_score = {1: 5, 2: 4, 3: 3}.get(min(ranks), 1) if ranks else 1
        hit = sum(any(alt.lower() in answer.lower() for alt in f.split("|")) for f in facts)
        response_score = 1 if refused else (5 if hit == len(facts) else 3 if hit else 1)
    else:             # out of scope: the correct behaviour is to refuse
        retrieval_score = 5 if r["low_confidence"] else 1
        response_score = 5 if refused else 1

    rows.append({"difficulty": difficulty, "question": question,
                 "top_score": r["top_score"], "low_conf": r["low_confidence"],
                 "retrieved": retrieved, "retrieval_score": retrieval_score,
                 "response_score": response_score, "answer": answer})

df = pd.DataFrame(rows)
print(df[["difficulty", "question", "top_score", "retrieval_score", "response_score"]])
print(df.groupby("difficulty")[["retrieval_score", "response_score"]].mean().round(2))
print("OVERALL:", df[["retrieval_score", "response_score"]].mean().round(2).to_dict())
print("\nNote: scores are an automatic first pass. Read test_results.csv and correct "
      "any generous score by hand (see README, 'Manual correction').")

df.to_csv("test_results.csv", index=False)
json.dump(rows, open("test_results.json", "w"), indent=2, ensure_ascii=False)
