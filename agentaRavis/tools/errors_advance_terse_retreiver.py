from libAgent.retriver import RetriverFactory
from agentaRavis.core.embeddings import embeddings
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.tools.retriever import create_retriever_tool
from libAgent.jsonFileToDocument import jsonFileToDocuments

INPUT_FILE = "./inputs/errorCodesAi.json"
DB_DIR = "./ChromaDB/errors_advance_terse"

chunks = jsonFileToDocuments(INPUT_FILE)

dense_retriever = RetriverFactory.createChromaRetriverMMR(
    embeddings=embeddings,
    dbPath=DB_DIR
)

bm25_retriever = RetriverFactory.createBM25RetrieverFromDocuments(chunks)

hybrid_retriever = EnsembleRetriever(
    retrievers=[dense_retriever, bm25_retriever],
    weights=[0.7, 0.3]
)

errors_advance_terse_retriever_tool = create_retriever_tool(
    retriever=hybrid_retriever,
    name="errors_advance_terse_retriever_tool",
    description=(
        "Use this tool to search the vector store for documentation related to "
        "Advance and Terse elevator control boards, including error codes, "
        "faults, failure descriptions, possible causes, troubleshooting guides, "
        "and recommended solutions. Advance and Terse are elevator control "
        "systems developed by Ravis Control Company. Queries should be in English."
    )
)
