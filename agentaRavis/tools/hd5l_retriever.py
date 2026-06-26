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
        """This knowledge base provides comprehensive technical documentation for the HD5L Series voltage-type PWM drive, specifically tailored for elevator applications.
        It covers the full lifecycle of the drive system, including safety protocols, mechanical and electrical installation, and environmental constraints such as temperature and grounding requirements.
        The content details extensive parameter configuration for motor control strategies, supporting V/f, Sensorless Vector Control, and Closed-loop Vector Control modes for both asynchronous and synchronous motors.
        Key features include auto-tuning procedures, encoder integration via SINCOS or UVW interfaces, and precise motion profile management with S-curve acceleration and jerk settings.
        The system supports advanced diagnostics, fault logging, and protection mechanisms like overheat and phase loss detection.
        Communication capabilities are defined through RS485 interfaces utilizing MODBUS RTU and ASCII protocols, with specific register mappings and error checking methods.
        Users can retrieve information on hardware specifications, I/O terminal wiring, keypad navigation, and troubleshooting common operational errors.
        This resource is well-suited for engineers and technicians seeking implementation guidelines, configuration parameters, and maintenance procedures for HD5L drive systems, ensuring safe and efficient elevator operation through detailed technical specifications and best practices.
        """
    )
)
