from libAgent.retriver import RetriverFactory
from agentaRavis.core.embeddings import embeddings
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.tools.retriever import create_retriever_tool
from libAgent.jsonFileToDocument import jsonFileToDocuments

INPUT_FILE = "./inputs/menu_advanceAi.json"
DB_DIR = "./ChromaDB/db_menu_advance"

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

menu_advance_retriever_tool = create_retriever_tool(
    retriever=hybrid_retriever,
    name="menu_advance_retriever_tool",
    description=(
        "Use this tool to search the vector store for documentation about "
        "Advance Board elevator controllers, including menus, parameters, "
        "configuration options, settings, and operating instructions. "
        "The Advance Board is an elevator control system developed by "
        "Ravis Control Company. Queries should be in English."
    )
)
