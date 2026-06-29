import logging

from pydantic import BaseModel, Field
import agentaRavis.core.config

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from agentaRavis.core.execution_state import build_execution_state
from agentaRavis.core.llmStateExecution import chainExecution
from agentaRavis.core.llms import llm
from agentaRavis.graph.builder import graph
from agentaRavis.schemas.history import LangChainHistoryMessage

from fastapi import FastAPI, WebSocket , WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio

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


def serialize_stream_chunk(chunk: dict) -> str:
    return json.dumps(chunk, default=str, ensure_ascii=False)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)

    current_task = None

    try:
        while True:
            data = await websocket.receive_text()

            # cancel previous run if still running
            if current_task and not current_task.done():
                current_task.cancel()

            async def run_graph():
                try:
                    async for chunk in graph.astream(
                        {
                            "query": data,
                            "history": [],
                            "messages": [],
                            "userid": str(client_id),
                        },
                        version='v2',
                        stream_mode="custom",
                    ):
                        await manager.send_personal_message(
                            serialize_stream_chunk(chunk['data']),
                            websocket,
                        )

                    await manager.send_personal_message(
                        json.dumps({"done": True}, ensure_ascii=False),
                        websocket,
                    )

                except asyncio.CancelledError:
                    return

                except Exception as e:
                    await manager.send_personal_message(
                        json.dumps({"error": str(e)}, ensure_ascii=False),
                        websocket,
                    )

            current_task = asyncio.create_task(run_graph())
        # while True:
        #     data = await websocket.receive_text()

        #     # try:
        #     #     payload = json.loads(data)
        #     # except json.JSONDecodeError:
        #     #     payload = {"query": data}

        #     # query = payload.get("query", data)
        #     # history = payload.get("history", [])
        #     # userid = payload.get("userid", str(client_id))

        #     async for chunk in graph.astream(
        #         {
        #             "query": 'hello',
        #             "history": [],
        #             "messages": [],
        #             "userid": '',
        #         },
        #         stream_mode="custom",
        #     ):
        #         await manager.send_personal_message(
        #             serialize_stream_chunk(chunk),
        #             websocket,
        #         )

        #     await manager.send_personal_message(
        #         json.dumps({"done": True}, ensure_ascii=False),
        #         websocket,
        #     )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        logger.exception("WebSocket error for client %s", client_id)
        manager.disconnect(websocket)


# def format_messages(messages):
#     output = []

#     for msg in messages:
#         if isinstance(msg, HumanMessage):
#             output.append(f"Human: {msg.content}")

#         elif isinstance(msg, AIMessage):
#             output.append(f"AI: {msg.content}")

#             if msg.tool_calls:
#                 output.append(f"Tool Calls: {msg.tool_calls}")

#         elif isinstance(msg, ToolMessage):
#             output.append(f"Tool Result: {msg.content}")

#     return "\n".join(output)
