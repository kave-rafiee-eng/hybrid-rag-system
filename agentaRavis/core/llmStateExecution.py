
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agentaRavis.core.llms import weekllm 
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an Agent Activity Reporter.

            Your task is to read an agent's execution history and produce a very short report of what happened.

            Rules:

            * Do not analyze the agent's reasoning.
            * Do not explain decisions.
            * Do not infer intentions.
            * Do not summarize tool outputs in detail.
            * Do not reproduce conversation content.
            * Mention tool names only when they were actually called.

            Output format:

            Agent Execution Report

            1. User request received.
            2. Agent use [tool_name].
            4. Agent called [tool_name] to obtain additional information.
            5. Agent processed the collected information.
            6. Agent generated the final response.

            Tools Used:

            * tool_1
            * tool_2

            Final Status:
            Completed successfully.

            """
        ),
        ("human", "{fullState}")
    ]
)

chainExecution = prompt |weekllm  | StrOutputParser()