import json
import os

import requests
from langchain_core.tools import tool

USER_API_URL = os.getenv(
    "API_USER_URL",
    "http://127.0.0.1:3000",
)
TICKET_API_TIMEOUT = float(os.getenv("TICKET_API_TIMEOUT", "15"))


def _ticket_response(response: requests.Response) -> str:
    response.raise_for_status()
    data = response.json() if response.content else {}
    return json.dumps({"success": True, "data": data}, ensure_ascii=False)


def _ticket_error(exc: Exception) -> str:
    if isinstance(exc, requests.Timeout):
        return json.dumps(
            {
                "success": False,
                "message": "Support ticket service timed out. Please try again later.",
            },
            ensure_ascii=False,
        )
    if isinstance(exc, requests.HTTPError):
        return json.dumps(
            {
                "success": False,
                "message": f"Support ticket service returned HTTP {exc.response.status_code}.",
                "detail": exc.response.text,
            },
            ensure_ascii=False,
        )
    return json.dumps(
        {
            "success": False,
            "message": f"Could not reach support ticket service: {exc}",
        },
        ensure_ascii=False,
    )


@tool
def create_ticket_for_support(
    question: str,
    user_id: str,
) -> str:
    """
    Create a support ticket for the RAVIS technical support team.

    Use this tool ONLY when the user has explicitly confirmed they want a support ticket
    registered (e.g. yes, ok, please do, بله).

    Do NOT use this tool proactively. First ask: "Would you like me to register a support
    ticket for you?" and wait for confirmation.

    Also use when the user directly and clearly asks to open or register a ticket.

    Args:
        user_id: Unique identifier of the user submitting the ticket.
        description: Detailed ticket body including symptoms, error codes, device model,
            steps already tried, and any relevant context from the conversation.

    Returns:
        A JSON string containing ticket creation status and response details from
        the support service.
    """
    payload = {
        "question": question,
    }

    try:
        response = requests.post(
            f"{USER_API_URL}/user/{user_id}/tickets",
            json=payload,
            timeout=TICKET_API_TIMEOUT,
        )
        return _ticket_response(response)
    except Exception as exc:
        return _ticket_error(exc)


@tool
def get_tickets_by_user_id(user_id: str) -> str:
    """
    Retrieve and track support tickets for a user.

    Use this tool when the user wants to follow up on previously submitted tickets, such as:
    - Checking ticket status (open, pending, answered, closed)
    - Seeing whether support has responded
    - Listing their registered tickets
    - Asking "what happened to my ticket?" or "was my ticket registered?"

    Do NOT use this tool to create a new ticket — use create_ticket_for_support instead.

    Args:
        user_id: Unique identifier of the user whose tickets should be retrieved.

    Returns:
        A JSON string containing the user's tickets and their current status.
    """
    try:
        response = requests.get(
            f"{USER_API_URL}/user/{user_id}/tickets",
            timeout=TICKET_API_TIMEOUT,
        )
        return _ticket_response(response)
    except Exception as exc:
        return _ticket_error(exc)
