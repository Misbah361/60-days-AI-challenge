# Day 10: Modular NLP Pipeline
A modular NLP pipeline (PreprocessingModule, VectorizerModule, Pipeline) that takes raw text and returns ranked similarity results.
Run: pip install nltk scikit-learn, then python nlp_pipeline.py

# Design Decision Note: Why Modular Beats Monolithic

I split the pipeline into PreprocessingModule, VectorizerModule and Pipeline, each with one job.

1. **Easier debugging.** If results look wrong, I can test each stage alone. Print `pre.transform(text)` to check cleaning, then check `vec.transform(query)` for scores. In one big script, a bug could be anywhere.
2. **Easier to extend.** To switch from TF-IDF to sentence embeddings, I only replace VectorizerModule. Preprocessing and Pipeline stay unchanged.
3. **Reusable and testable.** Each class can be unit-tested and reused in other projects (e.g. the Day 5 search engine).
4. **Clear error handling.** Validation sits in one place, so bad input fails early with a clear message instead of crashing deep inside scikit-learn.
5. **Safer teamwork.** Different people can work on different modules without breaking each other's code.

A monolithic script mixes cleaning, vectorising and ranking, so one small change can break everything and it is hard to find where.
