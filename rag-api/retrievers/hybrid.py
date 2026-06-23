# retrievers/hybrid.py
from langchain_classic.retrievers import EnsembleRetriever

class HybridRetrieverFactory:

    @staticmethod
    def create(vector_ret, bm25_ret):
        return EnsembleRetriever(
            retrievers=[vector_ret, bm25_ret],
            weights=[0.6, 0.4]
        )