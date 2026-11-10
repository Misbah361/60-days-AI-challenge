# Day 21: AI Product Quality Audit of the Day 20 Assistant

**System audited:** the Veridia Knowledge Assistant from Day 20 (FastAPI `/ask`, MiniLM + FAISS retrieval, Qwen2.5-1.5B-Instruct local model, 22-document fictional knowledge base, confidence gate at 0.3).
**Audit environment:** Google Colab, T4 GPU, deterministic decoding (`do_sample=False`).
**Method:** structured test suites per dimension, scored outcomes (not single responses), plus a manual read of every answer. Automatic keyword checks are only a first pass; where my reading disagreed with the check, the manual verdict is reported.

## Verdict

**Not ready for real users next week.** It is fast and accurate on well-formed questions (90% accuracy), but it breaks on realistic user phrasing (7/10 acceptable, only 4/10 clean) and its citations are not usable by non-technical users. It is ready for an **internal beta** with a human fallback. Three fixes (below) should be done before launch.

## 1. The five quality dimensions

| Dimension | One-sentence definition |
|---|---|
| Accuracy | The answer states the correct facts from the most current, relevant source. |
| Latency | The user gets an answer fast enough to feel interactive. |
| Reliability | The system gives consistent, error-free answers across rephrasings, typos, and unusual inputs. |
| Transparency | Every answer shows where it came from in a way a non-technical user can understand and act on. |
| Graceful degradation | When the knowledge base cannot answer, the system says so honestly instead of guessing or failing. |

## 2. Scorecard

Scores out of 5 are the manually adjusted pass rate scaled to 5, except transparency (judgement, see below).

| Dimension | Queries | Result | Score | Status |
|---|---|---|---|---|
| Accuracy | 10 | 9/10 pass | 4.5 / 5 | Pass |
| Latency | 10 | 0.69 s average, 1.39 s worst | 5 / 5 | Pass |
| Reliability | 10 | 10/10 automatic, **8/10 after manual read** | 4 / 5 | Partial |
| Transparency | 10 | **0/10 fully transparent** (citation present and correct in 10/10, readable in 0/10) | 1 / 5 | Fail |
| Graceful degradation | 5 | 5/5 honest, but with quality problems | 4 / 5 | Partial |
| Real user-style queries | 10 | 7/10 acceptable, 4/10 clean | 3.5 / 5 | Partial |

Transparency gets 1/5 rather than 0/5 because every answer does include a correct source; the failure is that no citation is understandable or actionable for a normal person.

## 3. Accuracy (10 structured queries)

Pass rule: all expected facts present and **no outdated fact** present (for example, a refund answer containing "14 days" fails).

**9/10 passed.** Single failure:
- *"What did release 3.0 launch?"* → "I don't have enough information". **Cause traced:** the correct chunk (`doc16-0`) ranked #1 but scored **0.258**, below the 0.3 confidence gate, so the model was never called. This is a false refusal caused by the threshold, not by retrieval or the model. Lowering the gate to about 0.25 would fix it but leaves almost no margin above out-of-scope scores (0.05 to 0.14 in this audit, up to 0.24 on Day 19).

## 4. Reliability (10 messy-input queries)

Inputs included typos ("refnd policy how many dayz"), shouting, one-word queries, extra whitespace, an emoji, and an empty string.

- Automatic check: **10/10**. No crashes; the empty string was refused cleanly.
- Manual read: **8/10**. Two answers ("refund" and "refund window 😀") began with the **marketing blurb** from `website.html` ("flexible plans with generous refund guarantees...") before reaching the real 30-day policy. They contain the right number, so they passed the keyword check, but the wording is not policy-grade.

## 5. Latency (10 queries, first warm-up call discarded)

| Pipeline component | Avg seconds | Share of total |
|---|---|---|
| Embed question | 0.0077 | 1.1% |
| FAISS search | 0.0001 | 0.0% |
| Version filter | 0.0000 | 0.0% |
| **LLM generation** | **0.6827** | **98.9%** |
| **Total (end to end)** | **0.6905** | 100% |

- Average end-to-end: **0.69 s**; fastest 0.41 s, slowest 1.39 s (spread is driven by answer length).
- **Slowest component: LLM generation**, by a wide margin.
- Cold start: the first call took 1.06 s versus 1.01 s warm, so cold-start cost is negligible here because the index is held in memory.
- Caveat: this is a 22-document index with a small local model on a GPU. A larger index or an API-hosted model would change the numbers.

## 6. Graceful degradation (5 queries absent from the knowledge base)

| Query | Top score | Outcome |
|---|---|---|
| Weather in Srinagar today | 0.134 | Refused (gate) |
| Who won the last cricket World Cup | 0.136 | Refused (gate) |
| How to bake a chocolate cake | 0.051 | Refused (gate) |
| How photosynthesis works | 0.045 | Refused (gate) |
| Veridia parental leave policy (plausible but absent) | 0.507 | Honest "does not provide specific details" from the model |

All five were honest; none answered from outside knowledge. The score gate caught the four clearly unrelated queries; only the grounding prompt stood between the plausible-but-absent question and a made-up answer (score 0.507 is far above the gate).

Quality problems found:
1. **Inconsistent wording:** gate refusals use one fixed sentence, the model's own refusal uses different wording.
2. **No next step:** "I don't have enough information in my knowledge base" does not tell the user who to contact.
3. **Misleading citation on a refusal:** the parental-leave answer was followed by `Sources: doc11-0 (website.html), doc13-0 (api_ref_2021.pdf), doc19-0 (careers.html)`, unrelated documents that look like evidence. Cause: the code only suppresses the Sources line when the answer starts with the exact refusal sentence.

## 7. Transparency (10 queries)

| Check | Result |
|---|---|
| Response includes a citation | 100% |
| The document that actually holds the answer is listed | 100% |
| Citation readable by a non-technical user | **0%** |
| Fully transparent (all three) | **0/10** |

Example of what users currently see: `Sources: doc1-0 (policy_2024.pdf), doc20-0 (billing_notes.txt), doc2-0 (website.html)`. Problems: internal chunk IDs (`doc1-0`), three sources listed when one supports the answer, file names rather than plain titles, and no dates, which matters in a knowledge base that contains outdated versions.

## 8. Ten user-style queries

Written the way a non-technical person would type them. Full answers are in `day21_user_style.csv`; answers below are shortened.

| # | User query | System answer (shortened) | Verdict |
|---|---|---|---|
| 1 | "hey so i bought the annual thing last week and changed my mind, can i get my money back or nah?" | Yes, within 30 days of purchase | Good |
| 2 | "how much is it" | Lists Starter $19, Pro $49, Enterprise custom | Good (did not guess a plan) |
| 3 | "Hi there, I'm trying to understand whether or not our team members are allowed to do their work from home at all, and if so how often...?" | Up to 3 days per week, then adds a claim about "restrictions" | Minor flaw (unsupported addition) |
| 4 | "is my stuff safe" | "Yes, your stuff is safe... bank-grade security" | **Fail:** over-promises from the marketing blurb, no concrete facts |
| 5 | "my api keeps giving me an error when i send lots of requests" | Rate limits and HTTP 429, then an irrelevant sentence about encryption | Minor flaw (right answer plus noise) |
| 6 | "do u guys have a phone number i can call at midnight" | "No, we do not have a phone number available for calling at midnight" | **Fail:** misleading; omits that Enterprise customers get 24/7 phone support |
| 7 | "whats new in the latest version" | Release 4.2: SAML single sign-on and dark mode | Good |
| 8 | "can i pay by card and is it secure" | Yes, card details tokenised, not stored on Veridia servers | Minor flaw ("you can pay by card" is an inference, no document lists payment methods) |
| 9 | "pricing pls" | Correct prices, then adds support hours "Monday to Friday, 10am to 5pm, email only" | **Fail:** outdated 2021 support hours leaked into the answer |
| 10 | "i deleted my account yesterday, when is my data actually gone?" | Purged from backups within 90 days | Good |

**Result: 4 clean, 3 acceptable with a flaw, 3 fails.** The same system scored 90% to 100% on engineered queries, so engineered tests overstate real-world quality.

**Root causes traced:**
- **#6:** retrieval worked (`doc9-0`, the 24/7 phone support document, ranked #1 at 0.364). The failure is **generation**: the model answered "no" without noting the Enterprise condition.
- **#9:** retrieval and filtering failed. The top three chunks were `pricing_2020.md` (0.421), `pricing_faq.md` (0.384), and `support_faq_2021.md` (0.192). The 2020 pricing document is not removed because its file name has no matching newer version name, and the 2021 support document stayed because its 2024 counterpart was not in the top results, so the version filter had nothing newer to prefer. A chunk scoring only 0.192 was still passed to the model, which blended it into the answer.

## 9. What passes and what fails

**Passes**
- Fast: 0.69 s average, dominated by the language model; retrieval is effectively free.
- Accurate on clear, well-formed questions (9/10), including picking the current policy over the old one.
- Robust to typos, shouting, whitespace, emoji, and empty input (no crashes).
- Never answered the four unrelated questions from its own knowledge.

**Fails**
- Citations unusable by non-technical users (0/10) and sometimes misleading (attached to a "no information" answer).
- Marketing text, outdated versions, or unsupported additions leak into 5 of the 20 realistic or messy-input answers.
- A correct document was rejected by the confidence gate (0.258 < 0.3).
- Inconsistent refusals with no next step.

## 10. Top three priorities if this launched to real users next week

**1. Stop wrong and misleading answers (highest risk).**
- Exclude `document_type = marketing` documents from policy and factual answers (the metadata already exists).
- Drop retrieved chunks that score far below the best one (for example under 60% of the top score) so weak chunks like the 0.192 support-hours document never reach the model.
- Add a `superseded_by` metadata field instead of matching file names, so `pricing_2020.md` and similar outdated documents are always removed.
- Tell the prompt to state conditions ("only Enterprise customers get 24/7 phone support") instead of answering a flat yes or no.

**2. Make citations usable.**
- Replace `doc1-0 (policy_2024.pdf)` with a plain-language source such as *"Refund policy, updated 10 Feb 2024"*.
- List only the sources that support the answer (one or two), not three.
- Never attach sources to a "no information" answer.

**3. Fix refusals and vague questions.**
- One consistent refusal message that includes a next step ("Contact support at ...").
- For vague questions ("is my stuff safe"), ask a clarifying question or answer with concrete facts rather than reassurance.
- Revisit the 0.3 gate: it caused one false refusal and cannot stop plausible-but-absent questions (score 0.507). Consider a lower gate with the grounding prompt as the main defence, or a reranker.

## 11. Limitations of this audit

- Small, fictional knowledge base (22 documents) and a 1.5B local model; results will not transfer directly to a production system.
- I wrote both the system and the tests, so test coverage reflects my own assumptions about what users ask.
- Automatic scoring is keyword-based; I corrected it by reading every answer, but those manual verdicts are subjective.
- Single deterministic run per query; no repeated trials or real users.
- Each dimension was tested with 10 queries, except graceful degradation, which used the 5 queries the task specified.

## Files

```
Day-21-Quality-Audit/
├── README.md                      # this report
├── Day21_Quality_Audit.ipynb      # notebook with all tests
├── day21_scorecard.csv
├── day21_accuracy.csv
├── day21_reliability.csv
├── day21_latency.csv
├── day21_transparency.csv
├── day21_degradation.csv
└── day21_user_style.csv           # full user-style outputs
```
