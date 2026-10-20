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
from starlette.requests import Request
from starlette.responses import Response
import json
import asyncio

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://109.125.149.108:3001",
]


def cors_headers(origin: str | None) -> dict[str, str]:
    allow_origin = origin if origin in ALLOWED_ORIGINS else (origin or "*")
    return {
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Max-Age": "600",
        "Vary": "Origin",
    }


@app.middleware("http")
async def ensure_cors(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=cors_headers(origin))
    response = await call_next(request)
    response.headers.update(cors_headers(origin))
    return response


# Last added middleware is outermost in FastAPI; keep CORS here too.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|109\.125\.149\.108)(:\d+)?",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
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
 
            payload = json.loads(data)

            agent_input = AgentInput(**payload)
                
            # cancel previous run if still running
            if current_task and not current_task.done():
                current_task.cancel()

            async def run_graph():
                try:
                    async for chunk in graph.astream(
                        {
                            "query": agent_input.query,
                            "history": agent_input.history,
                            "messages": [],
                            "userid": agent_input.userid,
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

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        logger.exception("WebSocket error for client %s", client_id)
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agentaRavis.main:app", host="0.0.0.0", port=8000, reload=True)


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
