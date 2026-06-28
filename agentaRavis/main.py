import logging

from pydantic import BaseModel, Field
import agentaRavis.core.config

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from agentaRavis.core.execution_state import build_execution_state
from agentaRavis.core.llmStateExecution import chainExecution
from agentaRavis.core.llms import llm
from agentaRavis.graph.builder import graph
from agentaRavis.schemas.history import LangChainHistoryMessage

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentInput(BaseModel):
    query: str
    executionReport: bool = False
    history: list[LangChainHistoryMessage] = Field(default_factory=list)
    userid : str

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/agent")
async def agentapi(data: AgentInput):

    if( len(data.history) > 20 ):
        return {
            "Execution": "",
            "answer": "تعداد پیام ها بیش از حد مجاز شده لطفا گفت و گوی جدید ایجاد کنید",
            'model':'system'
        }
    

    res = await graph.ainvoke({
        "query": data.query,
        "history": data.history,
        "messages": [],
        "userid":data.userid
    })

    execution = ""
    if data.executionReport:
        execution = await chainExecution.ainvoke({
            "fullState": build_execution_state(
                query=data.query,
                history=data.history,
                messages=res["messages"],
            )
        })

    last_ai = next(
        (msg for msg in reversed(res["messages"]) if isinstance(msg, AIMessage)),
        None,
    )

    return {
        "answer": last_ai.content if last_ai else "",
        "Execution": execution,
        'model':llm.model
    }

def format_messages(messages):
    output = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            output.append(f"Human: {msg.content}")

        elif isinstance(msg, AIMessage):
            output.append(f"AI: {msg.content}")

            if msg.tool_calls:
                output.append(f"Tool Calls: {msg.tool_calls}")

        elif isinstance(msg, ToolMessage):
            output.append(f"Tool Result: {msg.content}")

    return "\n".join(output)

# for event in graph.stream(
#     {"messages": [HumanMessage(content="what is error code 4 in advance board")]},
#     stream_mode="tasks"
# ):

#     pass
#     print("\n" + "-"*40)
    
#     task = {}
#     if 'name' in event:
#         # print(f"Task Name: {event['name']}")
#         task['name'] = event['name']
#     if 'input' in event:
#         # print("Status: Getting Input...")
#         task['input'] = "Getting Input..."
        
#     if 'result' in event and event['result']:
#         messages = event['result'].get('messages', [])
        
#         for msg in messages:
            
#             if isinstance(msg, AIMessage):
                
#                 if msg.tool_calls:
#                     # print("🛠 Tool Call Detected:")
#                     toolsCall = []
#                     for tool in msg.tool_calls:
#                         toolObj = {}
#                         toolObj['name'] = tool['name']
#                         toolObj['args'] = tool['args']
#                         # print(f"  - Tool: {tool['name']}")
#                         # print(f"  - Args: {tool['args']}")
#                         toolsCall.append( toolObj )
#                     if len( toolsCall ) :
#                         task['tools'] = toolsCall
#                 else :
#                     task['ai_resault'] = msg.content     
#             elif isinstance(msg , ToolMessage):
#                 task['tool_result'] = "tool create resault"
#     print(task)
