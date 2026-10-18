# Day 2: Your First Python AI Script

A first hands-on Python script in Google Colab that works with raw text, the same kind of data that NLP models learn from.

## What I did

The notebook has three cells:

1. **Cell 1**: ran the starter cell in Google Colab to confirm the environment works.
2. **Cell 2**: wrote a word-frequency counter that takes a sentence and counts how often each word appears.
3. **Cell 3**: cleaned the text by converting it to lowercase, stripping punctuation and normalizing whitespace.

## Files

| File | Description |
|---|---|
| `day02_first_python_script.ipynb` | Google Colab notebook with all three cells and their outputs |

## What I learned

- Python can count and clean text with only a few lines of code.
- Cleaning matters: "AI", "ai" and "AI!" count as three different words until the text is lowercased and punctuation is removed.
- This cleaning is the first step of text preprocessing, which Day 3 builds on with NLTK.

## Tools

Python, Google Colab
