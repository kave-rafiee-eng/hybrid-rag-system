from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from agentaRavis.core.llms import llm
from agentaRavis.graph.prompts import SYSTEM_PROMPT
from agentaRavis.graph.state import AgentState
from agentaRavis.schemas.history import history_to_messages
from agentaRavis.tools.registry import TOOLS


def init_state(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(history_to_messages(state.get("history", [])))
    messages.append(HumanMessage(content=state["query"]))
    return {"messages": messages}
def agent(state: AgentState):
    response = llm.bind_tools(TOOLS).invoke(
        state["messages"]
    )
    return {"messages": [response]}




def build_graph():
    graph = StateGraph(AgentState)

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
print(graph.get_graph().draw_ascii())