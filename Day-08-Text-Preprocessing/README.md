# Day 8: Text Preprocessing

## Task
Build a text preprocessing workflow that turns noisy real-world text into clean, structured tokens. I used three raw samples: a social media post, a news article and a customer review. Each contains punctuation, emojis, stopwords and inconsistent casing.

## Tools
Python, NLTK, Regex, pandas

## Pipeline
1. **Tokenisation:** word-level and sentence-level, using NLTK
2. **Stopword removal:** NLTK's built-in English stopword corpus, with vocabulary size compared before and after
3. **Punctuation stripping:** regex patterns (this also removes emojis and symbols)
4. **Stemming vs lemmatisation:** PorterStemmer and WordNetLemmatizer compared side by side
5. **Before/after comparison:** shown for every step across all three samples

## Files
- `Day8_Text_Preprocessing.ipynb`: the full notebook with outputs for every step

## Results
Stopword removal shrank the vocabulary by about 22% (social media), 27% (news) and 31% (review).

## Observations
- **Stopword removal can flip meaning.** "Would NOT recommend it" became `would recommend`, because "not" is in NLTK's stopword list. For sentiment tasks, negation words should be kept.
- **Contractions and numbers get mangled.** "can't" was split into `ca` and `n't`, and "$2.5" became `25` after the regex step.
- **Stemming vs lemmatisation.** Stemming is faster but crude and produces non-words (`movi`, `energi`, `cri`). Lemmatisation keeps real words, but without part-of-speech tags it often leaves words like "watched" unchanged.
- **The sentence tokenizer struggles with repeated punctuation.** "!!!" and emojis caused an odd split in the social media post.

## What I learned
Preprocessing steps are not harmless: each one trades noise for lost information. Good pipelines choose steps to fit the task, for example keeping "not" for sentiment analysis.
