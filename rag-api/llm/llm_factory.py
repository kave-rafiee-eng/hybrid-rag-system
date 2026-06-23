# llm/llm_factory.py
from langchain_openai import ChatOpenAI

class LLMFactory:

    @staticmethod
    def create_llm( model , base_url , api_key ):
        return ChatOpenAI(
            model=model ,
            temperature=0.3,
            base_url=base_url,
            api_key=api_key
        )