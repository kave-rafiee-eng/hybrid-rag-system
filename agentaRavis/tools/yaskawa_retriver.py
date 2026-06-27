from libAgent.markdownSplitter import markdownTextSplitter
from libAgent.retriver import RetriverFactory
from agentaRavis.core.embeddings import embeddings
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.tools.retriever import create_retriever_tool

INPUT_FILE = "./inputs/yaskawa-l1000a.txt"
DB_DIR = "./ChromaDB/db_yaskawa"

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
        """
        This knowledge base comprises comprehensive technical documentation for the Yaskawa L1000A variable frequency drive series, specifically addressing CIMR-LB and CIMR-LT models across 200V and 400V classes.
        It provides detailed guidance on mechanical installation, electrical wiring, and safety compliance, including strict protocols for grounding, capacitor discharge, and hazardous energy isolation. 
        The collection extensively covers drive configuration, detailing parameter setup for V/f, open-loop vector, closed-loop vector, and permanent magnet motor control modes. 
        Advanced operational features such as auto-tuning, encoder configuration, and elevator-specific logic—including rescue operations, leveling, and anti-rollback control—are thoroughly documented. 
        Users can retrieve information on troubleshooting fault codes, managing maintenance schedules for components like cooling fans and capacitors, and configuring communication protocols such as MEMOBUS/Modbus and CANopen. 
        The content supports technical depth ranging from hardware specifications and terminal assignments to complex control loop tuning and safety standard adherence like EN81 and UL/CE compliance. 
        This resource is well-suited for engineers and technicians seeking to install, configure, operate, and maintain these industrial drives, particularly in elevator applications requiring precise speed control and safety integration. 
        It excludes general consumer electronics or non-Yaskawa drive architectures.
        """
        "Queries should be in English."
    )
)
