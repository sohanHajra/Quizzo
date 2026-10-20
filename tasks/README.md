# Quizzo internals

The runnable entry point is the root-level [app.py](../app.py). The `tasks/` packages are small building blocks, retained to make the original 2024 structure understandable.

- `Document_Ingestion/`: uploaded PDF extraction, temporary file cleanup.
- `Embeddings/`: Vertex AI embedding adapter.
- `Data_Pipeline/`: chunk text and create the in-memory Chroma index.
- `Quiz_Generator/`: retrieve contextual chunks, generate questions, validate JSON and screen duplicates.
- `Quiz_Manager/`: quiz navigation; the root app persists answers in Streamlit session state.

The nested `tasks/App/app.py` is a **historical prototype**, not the supported entry point. It may not run against current dependencies. See the root README for the current execution and test commands. 
