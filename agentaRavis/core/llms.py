import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    # model="gpt-4.1-mini",
    # model='gpt-5-nano',
    # model='gpt-4o-mini',
    model="gapgpt-qwen-3.5-thinking",
    temperature=0.3,
    api_key=os.getenv("OPENAI_KEY"),
    base_url=os.getenv("BASE_URL"),
)



weekllm = ChatOpenAI(
    # model="gpt-4.1-mini",
    # model='gpt-5-nano',
    model="gapgpt-qwen-3.5",
    temperature=0.3,
    api_key=os.getenv("OPENAI_KEY"),
    base_url=os.getenv("BASE_URL"),
)