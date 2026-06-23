# retrievers/vector_store.py
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document


class RetriverFactory:

    @staticmethod
    def createChromaRetriverMMR(embeddings , dbPath:str , k=15, fetch_k=50, lambda_mult = 0.3 ):
        vStore = Chroma(
            embedding_function=embeddings,
            persist_directory=dbPath
        )

        dense_retriever = vStore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,
                "fetch_k": fetch_k,
                "lambda_mult": lambda_mult
            }
        )

        return dense_retriever
    
    @staticmethod
    def createBM25RetrieverFromDocuments(docs: list[Document],k=15):
        retriever = BM25Retriever.from_documents(docs)
        retriever.k = k
        return retriever
    

