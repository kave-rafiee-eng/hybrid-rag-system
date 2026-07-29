from libAgent.markdownSplitter import markdownTextSplitter
from libAgent.retriver import RetriverFactory
from agentaRavis.core.embeddings import embeddings
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.tools.retriever import create_retriever_tool

INPUT_FILE = "./inputs/qma-1200A.txt"
DB_DIR = "./ChromaDB/db_qma1200a"

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


qma_1200a_retriever_tool = create_retriever_tool(
    retriever=hybrid_retriever,
    name="qma_1200a_retriever_tool",
    description=(
        "Search technical documentation for the qma A1200 series elevator drive . "
        "qma A1200 is an AC motor drive controller designed for elevator applications. "
        "Queries should be in English."
        """
        This knowledge base centers on the qma A1200 elevator inverter family, delivering a cohesive reference for configuring, operating, and maintaining these drives in elevator applications. 
        It integrates hardware specifications, environmental and safety requirements, I/O wiring, grounding and EMI considerations, braking units and braking resistors, as well as the full parameterization framework used to tailor performance.
        Users can retrieve detailed guidance on encoder interfaces and compatible encoder types, PG card integrations, and the wiring schemes that connect main/control circuits, DI/AI/AO signaling, RS485, and other communication channels.
        The repository emphasizes control architectures (Sensorless and Feedback Vector, V/F), speed and torque tuning, autotuning procedures, S-curve acceleration/deceleration, preset speeds, and terminal mappings, including the mapping semantics of extensive function-code groups (P0–P9, PA–PD, PU, PP) and related safety and fault-handling semantics.
        It also covers application-specific flows such as inspection running, emergency/UPS-enabled operation, braking and zero-servo tuning, and fault data logging, with password-protected parameter access and practical sequences for maintenance and fault resolution.
        While highly technical and model-aware, the material sometimes presents partial data (e.g., some dimensions or model-specific defaults), requiring model/firmware context for precise values. Overall, it supports precise configuration, diagnostics, and procedural guidance for elevator drive deployments.
        """
    )
)
