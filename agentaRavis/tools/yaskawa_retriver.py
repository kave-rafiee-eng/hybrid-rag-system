from libAgent.markdownSplitter import markdownTextSplitter
from libAgent.retriver import RetriverFactory
from agentaRavis.core.embeddings import embeddings
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.tools.retriever import create_retriever_tool

INPUT_FILE = "./inputs/yaskawa-l1000a.txt"
DB_DIR = "./ChromaDB/db"

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


yaskawa_l1000a_retriever_tool = create_retriever_tool(
    retriever=hybrid_retriever,
    name="yaskawa_l1000a_search",
    description=(
        "Search technical documentation for the YASKAWA L1000A elevator drive, "
        "including parameters, fault codes, alarms, troubleshooting guides, "
        "configuration settings, wiring information, and operating instructions."
        "Queries should be in English."
    )
)
