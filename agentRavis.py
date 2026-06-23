from dotenv import load_dotenv
import os
load_dotenv()

from pathlib import Path

# -----------------------------
# Imports
# -----------------------------
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools.retriever import create_retriever_tool

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_classic.retrievers import EnsembleRetriever

from libAgent.markdownSplitter import markdownTextSplitter
from libAgent.retriver import RetriverFactory


# -----------------------------
# LLM + Embeddings
# -----------------------------
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=os.getenv("OPENAI_KEY"),
    base_url="https://api.openai.com/v1"
)

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_KEY"),
    base_url="https://api.openai.com/v1"
)

import json
errorCodesAi = []
with open("inputs/errorCodesAi.json", "r", encoding="utf-8") as f:
    errorCodesAi = json.load(f)

from langchain_core.tools import tool

@tool
def get_errorCode_by_code(code: str) -> str:
    """
    Get error code reason and solutions for RAVIS control advacne and terse board products.
    Returns a JSON string containing error details.
    """

    errorCode = next(
        (e for e in errorCodesAi if e["code"] == code),
        None
    )

    if errorCode is None:
        return json.dumps({
            "found": False,
            "code": code,
            "message": "Error code not found"
        })

    return json.dumps({
            "found": True,
            "data": errorCode
        }, ensure_ascii=False)
# -----------------------------
# Data + Retriever
# -----------------------------
INPUT_FILE = "./inputs/yaskawa-l1000a.txt"
DB_DIR = "./ChromaDB/db"

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


retriever_tool = create_retriever_tool(
    retriever=hybrid_retriever,
    name="yaskawa_l1000a_search",
    description="Search technical documentation about YASKAWA L1000A elevator drive"
)

tools = [retriever_tool,get_errorCode_by_code]


# -----------------------------
# Agent Node
# -----------------------------
def agent(state: MessagesState):
    messages = state["messages"]

    llm_with_tools = llm.bind_tools(tools)

    response = llm_with_tools.invoke(
        messages
    )

    return {"messages": [response]}

def init_state(state: MessagesState):

    SYSTEM_PROMPT = """
    You are a technical assistant .

    Rules:
    - Use tools when needed to find accurate technical information.
    - If tool results are useful, continue reasoning using them.
    - If enough information is gathered, answer clearly and stop calling tools.
    - If you are uncertain, use tools again.
    - Always prefer factual tool output over guessing.
    """
    return {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT)
        ]
    }

# -----------------------------
# Tool Node
# -----------------------------
tool_node = ToolNode(tools)


# -----------------------------
# LangGraph
# -----------------------------
graph_builder = StateGraph(MessagesState)

graph_builder.add_node("init", init_state)

graph_builder.add_node("agent", agent)
graph_builder.add_node("tools", tool_node)


graph_builder.add_edge(START, "init")
graph_builder.add_edge("init", "agent")

# Agent → Tools OR END
graph_builder.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)

# Tools → Agent (loop back)
graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile()


# -----------------------------
# Debug graph
# -----------------------------
print(graph.get_graph().draw_ascii())

# print(graph.invoke({'messages':[HumanMessage(content="what is error code 3 in advance board")]}))



from langchain_core.messages import AIMessage,ToolMessage

for event in graph.stream(
    {"messages": [HumanMessage(content="what is error code 4 in advance board")]},
    stream_mode="tasks"
):

    pass
    print("\n" + "-"*40)
    
    task = {}
    if 'name' in event:
        # print(f"Task Name: {event['name']}")
        task['name'] = event['name']
    if 'input' in event:
        # print("Status: Getting Input...")
        task['input'] = "Getting Input..."
        
    if 'result' in event and event['result']:
        messages = event['result'].get('messages', [])
        
        for msg in messages:
            
            if isinstance(msg, AIMessage):
                
                if msg.tool_calls:
                    # print("🛠 Tool Call Detected:")
                    toolsCall = []
                    for tool in msg.tool_calls:
                        toolObj = {}
                        toolObj['name'] = tool['name']
                        toolObj['args'] = tool['args']
                        # print(f"  - Tool: {tool['name']}")
                        # print(f"  - Args: {tool['args']}")
                        toolsCall.append( toolObj )
                    if len( toolsCall ) :
                        task['tools'] = toolsCall
                else :
                    task['ai_resault'] = msg.content     
            elif isinstance(msg , ToolMessage):
                task['tool_result'] = "tool create resault"
    print(task)