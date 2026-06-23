# retrievers/bm25.py
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

class BM25Factory:

    @staticmethod
    def create(texts: list[str]):
        docs = [Document(page_content=t) for t in texts]
        retriever = BM25Retriever.from_documents(docs)
        retriever.k = 5
        return retriever