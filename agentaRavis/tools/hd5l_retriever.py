from libAgent.markdownSplitter import markdownTextSplitter
from libAgent.retriver import RetriverFactory
from agentaRavis.core.embeddings import embeddings
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.tools.retriever import create_retriever_tool

INPUT_FILE = "./inputs/HD5L.txt"
DB_DIR = "./ChromaDB/db_hd5l"

chunks = markdownTextSplitter(INPUT_FILE)

dense_retriever = RetriverFactory.createChromaRetriverMMR(
    embeddings=embeddings,
    dbPath=DB_DIR
)

bm25_retriever = RetriverFactory.createBM25RetrieverFromDocuments(chunks)

hybrid_retriever = EnsembleRetriever(
    retrievers=[dense_retriever, bm25_retriever],
    weights=[0.7, 0.3]
)


hd5l_hpmont_retriever_tool = create_retriever_tool(
    retriever=hybrid_retriever,
    name="hd5l_hpmont_retriever_tool",
    description=(
        "Search technical documentation for the HD5L elevator drive manufactured by HPMONT. "
        "HD5L is an AC motor drive controller designed for elevator applications. "
        "Include information on parameters, fault codes, alarms, troubleshooting guides, "
        "configuration settings, wiring diagrams, and operating instructions. "
        "Queries should be in English."
    )
)
