import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    # model="gpt-4.1-mini",
    # model='gpt-5-nano',
    model='gpt-4o-mini',
    temperature=0.3,
    api_key=os.getenv("OPENAI_KEY"),
    base_url=os.getenv("BASE_URL"),
)

weekllm = ChatOpenAI(
    # model="gpt-4.1-mini",
    model='gpt-5-nano',
    temperature=0.3,
    api_key=os.getenv("OPENAI_KEY"),
    base_url=os.getenv("BASE_URL"),
)