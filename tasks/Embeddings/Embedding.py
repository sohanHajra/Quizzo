"""Small Vertex AI embedding adapter compatible with LangChain vector stores."""

from langchain_google_vertexai import VertexAIEmbeddings


class EmbeddingClient:
    def __init__(self, *, model_name="textembedding-gecko@003", project=None, location="us-central1"):
        self.client = VertexAIEmbeddings(model_name=model_name, project=project, location=location)

    def embed_query(self, query):
        return self.client.embed_query(query)

    def embed_documents(self, documents):
        return self.client.embed_documents(documents)
