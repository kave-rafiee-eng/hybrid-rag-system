# retrievers/vector_store.py
from langchain_chroma import Chroma

class VectorStoreFactory:

    @staticmethod
    def create(embeddings , dbPath ):
        return Chroma(
            embedding_function=embeddings,
            persist_directory= dbPath
        )