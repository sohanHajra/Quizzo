# Quizzo

**An early-college personal LLM project, revisited in 2026.** I built Quizzo while I was also interning at RadicalX, because generic quiz generation was not giving me the specific, well-framed questions I wanted from my own notes before exams. I wanted to upload the material I was actually studying, choose a topic, and test myself against that context instead of getting generic questions.

Quizzo remains a learning and portfolio prototype, **not a production learning platform**. Its original development dates to June 2024; the 2026 maintenance pass improved its reliability, configuration, tests, and documentation. This is not a claim that the 2026 refinements were present in the 2024 version.

## How it works

```text
student PDFs -> PyPDFLoader -> 1,000-character chunks (100 overlap)
             -> Vertex AI text embeddings -> in-memory Chroma index
topic -> retrieve relevant document chunks -> grounded Gemini prompt
      -> parse/validate JSON question -> filter duplicates -> Streamlit quiz
      -> persistent answers / feedback -> downloadable score PDF
```

The app uses **Python, Streamlit, LangChain, Google Vertex AI (Gemini and embeddings), Chroma, NLTK-inspired token n-gram similarity, and ReportLab**. It accepts PDF files and generates up to 10 multiple-choice questions with answers and explanations.

## Run it locally

Requires Python 3.10+ and a **Google Cloud project with Vertex AI access, supported model access, and Application Default Credentials**. Model availability and API compatibility change over time; test your configured models in your own project. Cloud API use may incur charges. No credentials are provided with the repository.

```bash
git clone https://github.com/sohanHajra/Quizzo.git
cd Quizzo
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"    # PowerShell: $env:GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export QUIZZO_LLM_MODEL="gemini-pro"              # Replace with a model available to your project
streamlit run app.py
```

Do not commit service-account JSON. Prefer short-lived, least-privilege credentials through ADC and protect document content. This prototype sends extracted text to Google Cloud AI services and stores vectors in a local in-memory collection.

## Verification

Offline tests cover question JSON/schema parsing and duplicate detection without cloud credentials.

```bash
python -m compileall -q app.py tasks
python -m unittest discover -s tests -v
```

A GitHub Actions workflow runs these checks on push and pull request. **Passing offline tests is not proof of working Vertex AI credentials, model availability, an end-to-end cloud run, or deployment uptime.**

## 2026 maintenance notes

- Replaced hard-coded credential paths/project placeholders with environment/ADC configuration.
- Bounded model-generation attempts; invalid/duplicate questions no longer retry forever.
- Validates JSON question shape, labels, answers, and explanations before displaying them.
- Passes retrieved document text explicitly into the prompt.
- Fixes quiz answer/score persistence across Streamlit reruns and keeps report generation in memory.
- Uses token rather than character n-gram similarity for duplicate screening.
- Cleans up temporary uploaded-PDF files even when ingestion fails.
- Added focused offline tests and checks workflow.

**Limitations:** This is not a pedagogical efficacy study. Similarity filtering does not guarantee question quality, retrieval does not eliminate model hallucinations, and structured output is checked for shape rather than factual correctness. Scanned PDFs without extractable text are not OCR'd. Only PDF input is supported. Multiple-choice generation depends on configured cloud-model access; the historical `gemini-pro` default may require replacement in a current Google Cloud project.

## A few things I'd test next

- Evaluate question relevance, answer faithfulness, and difficulty on a labeled set of study notes.
- Add explicit source/page citations and answer-verification checks.
- Improve document parsing and retrieval over tables/equations/scanned material.
- Add usage limits, accessibility checks, and privacy controls before serving other users.

## History and ownership

Personal project by **Sohan Hajra**, developed during early college, with original repository activity starting June 2, 2024. The 2026 revisit is a distinct maintenance pass.

MIT licensed. See [LICENSE](LICENSE).
