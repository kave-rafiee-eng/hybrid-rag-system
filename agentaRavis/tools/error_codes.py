
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