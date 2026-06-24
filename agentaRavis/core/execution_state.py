import json

from langchain_core.messages import BaseMessage

from agentaRavis.schemas.history import LangChainHistoryMessage, history_to_messages


def build_execution_state(
    query: str,
    history: list[LangChainHistoryMessage],
    messages: list[BaseMessage],
) -> str:
    history_count = len(history_to_messages(history))
    execution_messages = messages[1 + history_count:]

    return json.dumps(
        {
            "current_query": query,
            "current_execution": execution_messages,
        },
        default=str,
        ensure_ascii=False,
        indent=2,
    )
