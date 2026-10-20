
import os
from langchain_openai import  OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    # model="text-embedding-3-large",
    # api_key=os.getenv("OPENAI_KEY"),
    # base_url=os.getenv("BASE_URL"),
    model="Embedding-3-Large",
    api_key=os.getenv("ARVAN_API_KEY"),
    base_url="https://api.arvancloudai.ir/v1"
)