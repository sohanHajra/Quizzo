"""Quizzo: a document-grounded study quiz prototype (2026 maintenance revision)."""

import os
import streamlit as st

from tasks.Document_Ingestion.Document_Ingestion import DocumentProcessor
from tasks.Embeddings.Embedding import EmbeddingClient
from tasks.Data_Pipeline.data_pipeline import ChromaCollectionCreator
from tasks.Quiz_Generator.quiz_generator import QuizGenerator
from tasks.Quiz_Manager.quiz_manager import QuizManager

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


st.set_page_config(page_title="Quizzo", page_icon="📚")
st.title("Quizzo")
st.caption("Study the material you actually want to be tested on. Upload PDFs and generate a document-grounded quiz.")


def reset_quiz():
    for key in ("questions", "index", "answers"):
        st.session_state.pop(key, None)


def report_pdf(questions, answers):
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    total = len(questions)
    correct = sum(answers.get(i) == q["answer"] for i, q in enumerate(questions))
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(48, 750, "Quizzo | Quiz report")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(48, 716, f"Questions: {total}")
    pdf.drawString(48, 694, f"Answered: {len(answers)}")
    pdf.drawString(48, 672, f"Correct: {correct}")
    pdf.drawString(48, 650, f"Score: {100 * correct / total:.1f}%")
    pdf.save()
    return output.getvalue()


if "questions" not in st.session_state:
    with st.form("build"):
        processor = DocumentProcessor()
        processor.ingest_documents()
        topic = st.text_input("What should the quiz focus on?", placeholder="e.g. chapter 4, market structure")
        count = st.slider("Questions", 1, 10, 5)
        submitted = st.form_submit_button("Generate quiz")
    if submitted:
        if not processor.pages:
            st.error("Please upload at least one PDF with readable text.")
        else:
            try:
                project = os.getenv("GOOGLE_CLOUD_PROJECT") or None
                location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
                model = os.getenv("QUIZZO_LLM_MODEL", "gemini-pro")
                embeddings = EmbeddingClient(project=project, location=location)
                store = ChromaCollectionCreator(processor, embeddings).create_chroma_collection()
                with st.spinner("Generating document-grounded questions..."):
                    questions = QuizGenerator(topic, count, store, model_name=model).generate_quiz()
                st.session_state.update(questions=questions, index=0, answers={})
                st.rerun()
            except Exception as exc:
                st.error(f"Quiz generation failed: {exc}")
else:
    questions = st.session_state["questions"]
    index = st.session_state["index"]
    answers = st.session_state["answers"]
    manager = QuizManager(questions)
    item = manager.get_question_at_index(index)
    st.progress((index + 1) / len(questions))
    st.subheader(f"Question {index + 1} of {len(questions)}")
    st.write(item["question"])
    labels = {c["key"]: f'{c["key"]}) {c["value"]}' for c in item["choices"]}
    selection = st.radio("Select one answer", list(labels), format_func=labels.get,
                         index=None, key=f"answer_{index}", disabled=index in answers)
    if index not in answers:
        if st.button("Check answer", disabled=selection is None):
            answers[index] = selection
            st.rerun()
    else:
        is_correct = answers[index] == item["answer"]
        (st.success if is_correct else st.error)("Correct!" if is_correct else f'Correct answer: {item["answer"]}')
        st.write(item["explanation"])
    left, right = st.columns(2)
    if left.button("Previous", disabled=index == 0):
        st.session_state["index"] -= 1
        st.rerun()
    if right.button("Next", disabled=index == len(questions) - 1 or index not in answers):
        st.session_state["index"] += 1
        st.rerun()
    if len(answers) == len(questions):
        st.download_button("Download score report (PDF)", data=report_pdf(questions, answers),
                           file_name="quizzo-report.pdf", mime="application/pdf")
    if st.button("Build a new quiz"):
        reset_quiz()
        st.rerun()
