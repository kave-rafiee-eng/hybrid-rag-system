from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from agentaRavis.schemas.history import LangChainHistoryMessage


class AgentState(TypedDict):
    query: str
    history: list[LangChainHistoryMessage]
    messages: Annotated[list[BaseMessage], add_messages]