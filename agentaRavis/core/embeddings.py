
import os
from langchain_openai import  OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    # model="text-embedding-3-large",
    # api_key=os.getenv("OPENAI_KEY"),
    # base_url=os.getenv("BASE_URL"),
    model="Embedding-3-Large",
    api_key=os.getenv("ARVAN_API_KEY"),
    base_url="https://arvancloudai.ir/gateway/models/Embedding-3-Large/Ua02cuX3b4aq8ZhgyR0C3OFAg7O0cneTH-zojCzHpg7mPMJN1zUMbF0s1eA0OLwrGk9alnkvqo3fGcBkLjezBMgpGGqy44D8G2E3nLODf6KCf3HzComW4TssHOGKE9LWhdjlWjKJZfrBlGePdsdmZcMO1C1Je149W_3Zwjwpy-mB54Gbk_x_xnVRmc7Us04Q1UaAmTwG8EqOVJ5TeRPZYzOBtVCldBzwDvV6uYRjb9z1lxzh6oaSKJbd9k-K8VlczjhGbwX72ys/v1"
)