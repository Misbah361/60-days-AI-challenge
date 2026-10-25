"""Day 10: Modular end-to-end NLP pipeline.
PreprocessingModule = refactored Day 8 steps; VectorizerModule = refactored Day 9 TF-IDF + cosine similarity.
"""
import re
import numpy as np
import nltk
for pkg in ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']:
    nltk.download(pkg, quiet=True)
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class PreprocessingModule:
    """Day 8 steps chained: tokenise -> lowercase + stopwords -> strip punctuation -> stem/lemmatise.

    Parameters
    ----------
    use_lemma : bool, default True  - WordNetLemmatizer if True, PorterStemmer if False
    """
    def __init__(self, use_lemma=True):
        self.use_lemma = use_lemma
        self.stop_words = set(stopwords.words('english'))   # was a global in Day 8
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def tokenize(self, text):
        return word_tokenize(text)

    def remove_stopwords(self, tokens):
        lowered = [t.lower() for t in tokens]
        return [t for t in lowered if t not in self.stop_words]

    def strip_punct(self, tokens):
        # Removes punctuation/emojis so 'good', 'good!' and 'good!!!' become one feature
        cleaned = [re.sub(r'[^a-z0-9\s]', '', t) for t in tokens]
        return [t for t in cleaned if t.strip()]

    def normalise(self, tokens):
        if self.use_lemma:
            return [self.lemmatizer.lemmatize(t) for t in tokens]
        return [self.stemmer.stem(t) for t in tokens]

    def transform(self, text):
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        tokens = self.strip_punct(tokens)
        tokens = self.normalise(tokens)
        return ' '.join(tokens)


class VectorizerModule:
    """Day 9 TF-IDF + cosine similarity, split into fit / transform."""
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.doc_matrix = None

    def fit(self, corpus):
        self.doc_matrix = self.vectorizer.fit_transform(corpus)
        return self

    def transform(self, query):
        q_vec = self.vectorizer.transform([query])
        return cosine_similarity(q_vec, self.doc_matrix).flatten()


class Pipeline:
    """Chains validation -> PreprocessingModule -> VectorizerModule -> ranking."""
    def __init__(self):
        self.pre = PreprocessingModule()
        self.vec = VectorizerModule()

    @staticmethod
    def _validate(query):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query is empty. Please enter some text.")
        if len(query.strip()) == 1:
            raise ValueError("Query is a single character. Please enter a longer query.")
        if not re.search(r'[A-Za-z]', query):
            raise ValueError("Query has only numbers/symbols. Please include words.")

    def run(self, query, corpus, top_k=3):
        self._validate(query)
        clean_corpus = [self.pre.transform(d) for d in corpus]
        clean_query = self.pre.transform(query)
        if not clean_query:
            raise ValueError("Query has no meaningful words after cleaning (only stop words).")
        self.vec.fit(clean_corpus)
        scores = self.vec.transform(clean_query)
        idx = np.argsort(scores)[::-1][:top_k]
        return [(corpus[i], float(scores[i])) for i in idx]


if __name__ == "__main__":
    corpus = [
        "Python is a popular programming language for data science.",
        "Machine learning models learn patterns from data.",
        "Neural networks are inspired by the human brain.",
        "The cat sat on the warm windowsill all afternoon.",
        "Dogs are loyal pets and love long walks in the park.",
        "Pasta with tomato sauce is a classic Italian dish.",
        "Baking bread requires flour, water, yeast and patience.",
        "The stock market fell sharply after the interest rate news.",
        "Investors are worried about inflation and rising prices.",
        "Football fans filled the stadium for the championship match.",
        "The striker scored two goals in the second half.",
        "Natural language processing helps computers understand text.",
        "Deep learning needs large datasets and powerful GPUs.",
        "Fresh vegetables and fruits are part of a healthy diet.",
        "The central bank raised rates to control inflation.",
    ]
    pipe = Pipeline()

    queries = [
        "How do computers learn from data?",
        "my pet loves going outside",
        "economy and inflation news",
        "cooking italian food",
        "who won the football game?",
    ]
    print("=== 5 QUERY TESTS ===")
    for q in queries:
        print(f"\nQuery: {q}")
        for i, (doc, s) in enumerate(pipe.run(q, corpus), 1):
            print(f"  {i}. [{s:.3f}] {doc}")

    print("\n=== EDGE CASES ===")
    for case in ["", "a", "12345 !!! ???", "the and of"]:
        try:
            pipe.run(case, corpus)
            print(f"{case!r}: no error (unexpected)")
        except ValueError as e:
            print(f"{case!r}: handled -> {e}")
