from libAgent.markdownSplitter import markdownTextSplitter
from libAgent.retriver import RetriverFactory
from agentaRavis.core.embeddings import embeddings
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.tools.retriever import create_retriever_tool

INPUT_FILE = "./inputs/hevos.txt"
DB_DIR = "./ChromaDB/db_hevos"

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


hevos_retriever_tool = create_retriever_tool(
    retriever=hybrid_retriever,
    name="hevos_retriever_tool",
    description=(
        "Search technical documentation for the HEVOS hydraulic elevator control board"
        "Queries should be in English."
        """
        This knowledge base comprehensively addresses the installation, configuration, operation, and maintenance of hydraulic elevator systems centered on the HEVOS HE valve group and the SCH001 electronic control board. 
        It covers detailed safety procedures, regulatory compliance with EN81-20, EN81-50, and EU Lift Directive 2014/33/UE standards, and emergency protocols including unintended car movement prevention and manual lowering operations. 
        Users can retrieve extensive technical information about hydraulic components—such as pumps, valves, sensors, and flow meters—and their integration with electronic controls, including signal management (digital inputs/outputs), CAN bus communication, and multi-valve hierarchical architectures. 
        The material supports advanced troubleshooting via error codes, diagnostics, and self-control methods, as well as parameter configuration for motion control, speed, acceleration, and valve sequencing. 
        It also provides guidance for installation environment conditions, electrical panel setup, firmware updates, and maintenance tasks with spare parts identification and certification details. Additionally, the knowledge base includes in-depth discussions on application interfaces like the HEVOS app and Wi-Fi connectivity for real-time monitoring and parameter synchronization. 
        While highly technical and suited for elevator system engineers and technicians, the content focuses primarily on hydraulic elevator valve groups and their electronic control rather than broader elevator subsystems or non-hydraulic technologies.
        """
    )
)
