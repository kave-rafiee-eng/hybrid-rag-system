from agentaRavis.tools.error_codes import get_errorCode_by_code
from agentaRavis.tools.yaskawa_retriver import yaskawa_l1000a_retriver_tool

TOOLS = [
    get_errorCode_by_code,
    yaskawa_l1000a_retriver_tool
]