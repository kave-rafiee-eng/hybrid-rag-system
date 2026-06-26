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
        """This knowledge base provides comprehensive technical documentation for the Hpmont HD5L Series elevator drive controller.
        It covers the full lifecycle of the device, including mechanical installation, electrical wiring, and safety compliance with IEC standards. 
        The content details hardware specifications for I/O boards, encoder interfaces (SINCOS, UVW, ABZ), and peripheral components like braking resistors and reactors.
        A significant portion is dedicated to advanced parameter configuration, focusing on motor control algorithms such as V/f, Sensorless Vector Control (SVC), and Closed-loop Vector Control, with specific tuning for asynchronous and synchronous motors. 
        It also extensively documents the MODBUS communication protocol, including RTU/ASCII frame structures and register mapping. 
        Users can retrieve information on troubleshooting fault codes, managing elevator-specific features like inspection and battery-driven modes, performing auto-tuning, and adhering to maintenance and EMC guidelines. 
        The scope is strictly limited to the HD5L series hardware and its associated software parameters.
        """
    )
)
