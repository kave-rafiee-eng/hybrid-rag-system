# llm/embedding_factory.py
from langchain_openai import OpenAIEmbeddings

class EmbeddingFactory:

    @staticmethod
    def create( model , base_url , api_key ):
        return OpenAIEmbeddings(
            model= model,
            api_key= api_key,
            base_url= base_url
        )