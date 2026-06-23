from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from agentaRavis.core.llms import llm
from agentaRavis.graph.prompts import SYSTEM_PROMPT
from agentaRavis.tools.registry import TOOLS

from langchain_core.messages import SystemMessage


def agent(state: MessagesState):
    response = llm.bind_tools(TOOLS).invoke(
        state["messages"]
    )
    return {"messages": [response]}


def init_state(_):
    return {
        "messages": [SystemMessage(content=SYSTEM_PROMPT)]
    }


def build_graph():
    graph = StateGraph(MessagesState)

    graph.add_node("init", init_state)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "init")
    graph.add_edge("init", "agent")

    graph.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            "__end__": END
        }
    )

    graph.add_edge("tools", "agent")

    return graph.compile()


graph = build_graph()