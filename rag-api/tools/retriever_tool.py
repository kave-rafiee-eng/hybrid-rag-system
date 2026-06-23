# tools/retriever_tool.py
from langchain_core.tools.retriever import create_retriever_tool

class ToolFactory:

    @staticmethod
    def create_retriever_tool(retriever):
        return create_retriever_tool(
            retriever=retriever,
            name="retriever_hd5l",
            description="search in vector sotre about HD5L VFD drive only use english query"
        )