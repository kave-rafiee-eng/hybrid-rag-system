import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    # model="gpt-4.1-mini",
    # model='gpt-5-nano',
    # model='gpt-4o-mini',
    # model="gapgpt-qwen-3.5-thinking",
    model="GPT-4.1-Mini",
    # model="qwen3-235b-a22b",
    # model = 'deepseek-v4-flash',

    base_url="https://arvancloudai.ir/gateway/models/GPT-4.1-Mini/9OsdnLiTU_iiXBZwpOK3QzWFW__ES_uGi7PC7EgYnYjuy3VfT4wF1Q73FmlXRh35hbgUWSFYxHRQ1_bwbm6kO58L2TFGJf8JJxv---mUmUHRhMLNZrXkaUsEzftOvnK__6KmJnVF3HLhy_jR3zqUf6l-Lfp3TSMuKL4rs3S7wor8dqYBpcm-GTvr5MmrCupgVGuinj7ERK-PrM6kJBtCh1kOmMISB1zijOWLcR9QuLN__4et7J3JiDKqkXyhPA/v1",
    api_key=os.getenv("ARVAN_API_KEY"),

    # api_key=os.getenv("OPENAI_KEY"),
    # base_url=os.getenv("BASE_URL"),
)



weekllm = ChatOpenAI(
    # model="gpt-4.1-mini",
    # model='gpt-5-nano',
    # model="gapgpt-qwen-3.5",
    model="GPT-4.1-Mini",
    temperature=0.3,
    # api_key=os.getenv("OPENAI_KEY"),
    # base_url=os.getenv("BASE_URL"),
    base_url="https://arvancloudai.ir/gateway/models/GPT-4.1-Mini/9OsdnLiTU_iiXBZwpOK3QzWFW__ES_uGi7PC7EgYnYjuy3VfT4wF1Q73FmlXRh35hbgUWSFYxHRQ1_bwbm6kO58L2TFGJf8JJxv---mUmUHRhMLNZrXkaUsEzftOvnK__6KmJnVF3HLhy_jR3zqUf6l-Lfp3TSMuKL4rs3S7wor8dqYBpcm-GTvr5MmrCupgVGuinj7ERK-PrM6kJBtCh1kOmMISB1zijOWLcR9QuLN__4et7J3JiDKqkXyhPA/v1",
    api_key=os.getenv("ARVAN_API_KEY"),
)