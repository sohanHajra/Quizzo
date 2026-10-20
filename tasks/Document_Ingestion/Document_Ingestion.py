"""PDF ingestion and temporary-file cleanup."""

import os
import tempfile

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader


class DocumentProcessor:
    def __init__(self):
        self.pages = []

    def ingest_documents(self):
        uploaded = st.file_uploader(
            "Upload your study notes (PDF)", type=["pdf"], accept_multiple_files=True
        )
        self.pages = []
        for file in uploaded or []:
            path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
                    temp.write(file.getvalue())
                    path = temp.name
                self.pages.extend(PyPDFLoader(path).load())
            finally:
                if path and os.path.exists(path):
                    os.unlink(path)
        if uploaded:
            st.caption(f"Extracted {len(self.pages)} page(s) from {len(uploaded)} PDF(s).")
        return self.pages
