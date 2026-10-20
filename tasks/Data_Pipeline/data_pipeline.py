"""Build an in-memory Chroma index from uploaded document pages."""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma


class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        self.processor = processor
        self.embed_model = embed_model
        self.db = None

    def create_chroma_collection(self):
        if not self.processor.pages:
            raise ValueError("Upload one or more readable PDFs before generating a quiz.")
        chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(self.processor.pages)
        if not chunks:
            raise ValueError("No extractable text was found in the uploaded PDFs.")
        self.db = Chroma.from_documents(chunks, self.embed_model)
        return self.db
