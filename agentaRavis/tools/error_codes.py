
import json
errorCodesAi = []
with open("inputs/errorCodesAi.json", "r", encoding="utf-8") as f:
    errorCodesAi = json.load(f)

from langchain_core.tools import tool

@tool
def get_errorCode_by_code(code: str) -> str:
    """
    Get the reason and recommended solutions for error codes related to
    RAVIS Control Advance and Terse elevator control boards.

    Advance and Terse are elevator control boards developed by RAVIS Control.

    The `code` parameter represents an error code displayed on the LCD,
    7-segment display, or other indicators when the system detects a fault.

    Returns:
        A JSON string containing the error code details, possible causes,
        and recommended solutions.
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