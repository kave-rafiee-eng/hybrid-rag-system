import json
import logging
import os

import requests
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

USER_API_URL = os.getenv(
    "API_USER_URL",
    "http://127.0.0.1:3000",
)
AGENT_MEMORY_API_TIMEOUT = float(os.getenv("AGENT_MEMORY_API_TIMEOUT", "15"))


def _memory_response(response: requests.Response) -> str:
    response.raise_for_status()
    data = response.json() if response.content else {}
    return json.dumps({"success": True, "data": data}, ensure_ascii=False)


def _memory_error(exc: Exception) -> str:
    if isinstance(exc, requests.Timeout):
        return json.dumps(
            {
                "success": False,
                "message": "Agent memory service timed out. Please try again later.",
            },
            ensure_ascii=False,
        )
    if isinstance(exc, requests.HTTPError):
        return json.dumps(
            {
                "success": False,
                "message": f"Agent memory service returned HTTP {exc.response.status_code}.",
                "detail": exc.response.text,
            },
            ensure_ascii=False,
        )
    return json.dumps(
        {
            "success": False,
            "message": f"Could not reach agent memory service: {exc}",
        },
        ensure_ascii=False,
    )


def fetch_user_memory(user_id: str) -> str:
    if not user_id:
        return ""

    try:
        response = requests.get(
            f"{USER_API_URL}/user/{user_id}",
            timeout=AGENT_MEMORY_API_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json() if response.content else {}
        return data.get("agentMemory") or ""
    except Exception as exc:
        logger.warning("Failed to fetch user memory for %s: %s", user_id, exc)
        return ""


@tool
def update_long_term_memory(user_id: str, memory: str) -> str:
    """
    Update the long-term memory for a user.

    Use this tool when the user shares durable information worth remembering across
    future conversations, such as:
    - Installed devices, board models, or drive types
    - Site name, building, or project details
    - Recurring issues or preferences
    - Important technical context that should persist

    The backend replaces the stored memory entirely, so always send the FULL updated
    memory text: keep relevant existing facts from the conversation context and add
    new ones. Do not send only the new fragment.

    Do NOT store temporary troubleshooting steps, one-time questions, or sensitive
    credentials.

    Args:
        user_id: Unique identifier of the user.
        memory: Complete updated long-term memory text for this user.

    Returns:
        A JSON string with the saved memory record.
    """
    try:
        response = requests.patch(
            f"{USER_API_URL}/user/{user_id}",
            json={"agentMemory": memory},
            timeout=AGENT_MEMORY_API_TIMEOUT,
        )
        return _memory_response(response)
    except Exception as exc:
        return _memory_error(exc)
