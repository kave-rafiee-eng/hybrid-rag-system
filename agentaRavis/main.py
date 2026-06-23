
import json
from pydantic import BaseModel
import agentaRavis.core.config 

from langchain_core.messages import AIMessage, HumanMessage,ToolMessage
from agentaRavis.core.llmStateExecution import chainExecution
from agentaRavis.graph.builder import graph

import asyncio
from fastapi import FastAPI , WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationInput(BaseModel):
    query: str
    executionReport:bool

@app.post("/agent")
async def agentapi(data: TranslationInput):

    res = await graph.ainvoke({'messages':[HumanMessage(content=data.query)]})

    execution = ''
    if data.executionReport : 
        execution = await chainExecution.ainvoke({
            "fullState": json.dumps(
                res["messages"],
                default=str,
                ensure_ascii=False,
                indent=2
            )
        })

    return {
        'answer':res["messages"][-1].content,
        'Execution':execution
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
