from typing import Annotated, Literal, Union

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from pydantic import BaseModel, Field

class LangChainHumanMessage(BaseModel):
    type: Literal["human"] = "human"
    content : str


class LangChainAiMessage(BaseModel):
    type: Literal["ai"] = "ai"
    content : str


LangChainHistoryMessage = Annotated[
    Union[LangChainHumanMessage, LangChainAiMessage],
    Field(discriminator="type"),
]


def history_to_messages(history: list[LangChainHistoryMessage]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for item in history:
        if item.type == "human":
            messages.append(HumanMessage(content=item.content))
        else:
            messages.append(AIMessage(content=item.content))
    return messages
