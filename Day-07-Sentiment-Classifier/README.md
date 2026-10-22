# Day 7: Your First Classifier

A sentiment classifier that labels movie reviews as **positive** or **negative**, built with scikit-learn.

## Approach
- **Dataset:** NLTK `movie_reviews` (2,000 reviews, 1,000 positive and 1,000 negative)
- **Split:** 80% train (1,600) and 20% test (400), stratified
- **Model:** TF-IDF (unigrams and bigrams, stop words removed) with Logistic Regression

## Results
- **Test accuracy: 81.2%**
- Precision and recall are balanced (about 0.80 to 0.84) for both classes
- Confusion matrix: 157 true negatives, 168 true positives, 43 false positives, 32 false negatives

## 5 Manual Test Cases (2/5 correct)

| Review | Truth | Prediction |
|---|---|---|
| "An absolutely brilliant film, I loved every minute of it." | positive | positive ✅ |
| "Boring, predictable and way too long. A total waste of time." | negative | negative ✅ |
| "The acting was great but the story made no sense at all." | negative | positive ❌ (mixed sentiment) |
| "Not bad at all, I was pleasantly surprised." | positive | negative ❌ (negation) |
| "Oh great, another sequel nobody asked for. Just wonderful." | negative | positive ❌ (sarcasm) |

## Reflection
TF-IDF with Logistic Regression is a bag-of-words model. It adds up word weights and ignores word order, negation and tone. That is why it fails on mixed reviews, "not bad" and sarcasm.

The model also learned dataset quirks. Movie titles such as `mulan` and `truman` ended up as top positive words, so it partly memorised the data instead of learning pure sentiment.

**Improvements:** sentence embeddings or a transformer for context, more diverse training data, and negation-aware features.

## Files
- `Day7_Sentiment_Classifier.ipynb`: training code, evaluation, manual tests and reflection
- `sentiment_model.joblib`: the trained model

## Run it
```bash
pip install scikit-learn nltk joblib
```
Open the notebook and run all cells.

*Part of my 60 Day AI Challenge on Klymb.AI.*
