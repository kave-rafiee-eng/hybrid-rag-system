from tkinter.constants import S
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from agentaRavis.core.llms import llm
from agentaRavis.graph.prompts import SYSTEM_PROMPT
from agentaRavis.graph.state import AgentState
from agentaRavis.schemas.history import history_to_messages
from agentaRavis.tools.longTermMemory import fetch_user_memory
from agentaRavis.tools.registry import TOOLS

from langgraph.config import get_stream_writer
import json


def _safe_stream_payload(value) -> dict:
    return json.loads(json.dumps(value, default=str))


def init_state(state: AgentState):

    my_stream_writer = get_stream_writer()
    my_stream_writer({"init_state": type(state["history"])})

    userid = state.get("userid") or ""
    memory = fetch_user_memory(userid)

    system_parts = [SYSTEM_PROMPT.strip()]
    if userid:
        system_parts.append(f"User context:\n- userid: {userid}")
    if memory:
        system_parts.append(
            "Long-term user memory (facts from past conversations):\n"
            f"{memory}"
        )

    messages = [SystemMessage(content="\n\n".join(system_parts))]
    messages.extend(history_to_messages(state.get("history", [])))
    messages.append(HumanMessage(content=state["query"]))
    return {"messages": messages}

async def agent(state: AgentState):
    writer = get_stream_writer()

    llm_with_tools = llm.bind_tools(TOOLS)
    response = None

    async for event in llm_with_tools.astream_events(state["messages"], version="v2"):
        
        if event.get("event") == "on_chat_model_stream":
            content = event['data']['chunk'].content
            tool_call_chunks = event['data']['chunk'].tool_call_chunks
            response_metadata = event['data']['chunk'].response_metadata
            if len(tool_call_chunks) == 0 :
                finish_reason = response_metadata.get("finish_reason")

                if finish_reason is not None:
                    writer({"finish_reason": finish_reason})
                elif len(content) > 0 :
                    writer({"on_stream": content})
            else :
                writer({"too_call": True})

        if event.get("event") == "on_chat_model_end":
            response = event.get("data", {}).get("output")

    # writer({"response": response})
    # response = llm_with_tools.invoke(state["messages"])

    return {"messages": [response]}
#content='' additional_kwargs={} response_metadata={'model_provider': 'openai'} id='lc_run--019f1475-a8fb-72c2-86bc-4e112a6a774d' tool_calls=[] invalid_tool_calls=[{'name': None, 'args': 'code', 'id': None, 'error': None, 'type': 'invalid_tool_call'}] tool_call_chunks=[{'name': None, 'args': 'code', 'id': None, 'index': 0, 'type': 'tool_call_chunk'}]
# "content='' additional_kwargs={} response_metadata={'finish_reason': 'stop', 'model_name': 'gpt-5-mini', 'service_tier': 'default', 'model_provider': 'openai'} id='lc_run--019f147e-ab57-7180-bb51-f9ca7ac1c313' tool_calls=[] invalid_tool_calls=[] tool_call_chunks=[]"
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