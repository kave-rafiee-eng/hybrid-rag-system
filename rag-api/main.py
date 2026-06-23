# main.py
import json

from llm.llm_factory import LLMFactory
from llm.embedding_factory import EmbeddingFactory

from retrievers.vector_store import VectorStoreFactory
from retrievers.bm25 import BM25Factory
from retrievers.hybrid import HybridRetrieverFactory

from tools.retriever_tool import ToolFactory

from agents.graph import AgenticRag

from dotenv import load_dotenv
import os


load_dotenv('.env')
class Settings:
    OPENAI_API_KEY = 
    BASE_URL = "https://api.gapgpt.app/v1"

    EMBEDDING_API_KEY = 
    EMBEDDING_BASE_URL = "https://models.github.ai/inference"
    EMBEDDING_MODEL = "openai/text-embedding-3-small"

    DB_DIR = "../dist/db"
    SUMMARY_PATH = "../dist/summeries.json"


# init
llm = LLMFactory.create_llm( model="gpt-4.1-mini" , 
                            base_url=Settings.BASE_URL , 
                            api_key=Settings.OPENAI_API_KEY )
emb = EmbeddingFactory.create( model=Settings.EMBEDDING_MODEL,
                               base_url= Settings.EMBEDDING_BASE_URL,
                               api_key=Settings.EMBEDDING_API_KEY
                              )

# load data
summarize_text = []
with open(Settings.SUMMARY_PATH) as f:
    summarize_text = json.load(f)

# retrievers
vstore = VectorStoreFactory.create(emb , Settings.DB_DIR )
vector_ret = vstore.as_retriever()

bm25 = BM25Factory.create(summarize_text)

hybrid = HybridRetrieverFactory.create(vector_ret, bm25)

# tools
tool = ToolFactory.create_retriever_tool(hybrid)

# agent
agentClass = AgenticRag(llm, [tool])
graph = agentClass.build()

print( graph.get_graph().draw_ascii() )

# for event in graph.stream(
#     {"messages": "what is Slip compensation gain hd5l"},
#     stream_mode="updates"
# ):
#     print(event)
                
#uvicorn main:app --reload
from fastapi import FastAPI,WebSocket, WebSocketDisconnect

app = FastAPI()

# @app.post("/")
# def creatItem(userQuestion:str):
#     res = graph.invoke( {"messages": [userQuestion]} )
#     return res["messages"][-1]


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await invokeChainStream(data , websocket )
            # res = graph.invoke( {"messages": [data]} )
            # print(res["messages"][-1].content)
            # await manager.send_personal_message(res["messages"][-1].content, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

from langchain_core.messages import AIMessage,ToolMessage,HumanMessage

async def invokeChainStream( question , websocket:WebSocket):
    
    start = {"cmd":"start"}
    await manager.send_personal_message(  json.dumps( start , ensure_ascii=False) , websocket)
    
    for event in graph.stream(
        {"messages": [HumanMessage(content=question)]},
        stream_mode="tasks"
    ):
        task = {}
        if 'name' in event:
            task['name'] = event['name']
        if 'input' in event:
            task['input'] = "Getting Input..."
            
        if 'result' in event and event['result']:
            messages = event['result'].get('messages', [])
            for msg in messages:
                if isinstance(msg, AIMessage):
                    if msg.tool_calls:
                        toolsCall = []
                        for tool in msg.tool_calls:
                            toolObj = {}
                            toolObj['name'] = tool['name']
                            toolObj['args'] = tool['args']
                            toolsCall.append( toolObj )
                        if len( toolsCall ) :
                            task['tools'] = toolsCall
                    else :
                        task['ai_resault'] = msg.content     
                elif isinstance(msg , ToolMessage):
                    task['tool_result'] = "tool create resault"
                    
        await manager.send_personal_message(  json.dumps( task , ensure_ascii=False) , websocket)
        
# # run
# for event in graph.stream(
#     {"messages": "what is Slip compensation gain hd5l"},
#     stream_mode="updates"
# ):
#     print(event)