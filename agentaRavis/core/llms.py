import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    # model="gpt-4.1-mini",
    # model='gpt-5-nano',
    # model='gpt-4o-mini',
    # model="gapgpt-qwen-3.5-thinking",
    model="Qwen3.5",
    # model="qwen3-235b-a22b",
    # model = 'deepseek-v4-flash',

    # base_url="https://arvancloudai.ir/gateway/models/GPT-4.1-Mini/9OsdnLiTU_iiXBZwpOK3QzWFW__ES_uGi7PC7EgYnYjuy3VfT4wF1Q73FmlXRh35hbgUWSFYxHRQ1_bwbm6kO58L2TFGJf8JJxv---mUmUHRhMLNZrXkaUsEzftOvnK__6KmJnVF3HLhy_jR3zqUf6l-Lfp3TSMuKL4rs3S7wor8dqYBpcm-GTvr5MmrCupgVGuinj7ERK-PrM6kJBtCh1kOmMISB1zijOWLcR9QuLN__4et7J3JiDKqkXyhPA/v1",
    # base_url="https://arvancloudai.ir/gateway/models/GPT-5.6-Luna/ejWHZy5NG2ldzEn_WTm79YyoQR2RVOPQfn0tHnjQaW1INK2SN3z4iz7wJkV0ogxI0cM5ub-TZegRpsdk1b74cSDT0Hmre7wyGhk8ZgfWkfNz7CMt2OeqzfaTX9AoDlHdYeTGUnESnYntsrsIlVro8o9Vb3dkgjU5zVUlvhwKTim39BZm7v4SaY2kA9TpE_EJSBg3RVM5zIPuW3kO1tm5VczwyZ0ovzk0x5dYl9jF6AFN_8pm-ECGD2_dvYb93A/v1",
    base_url="https://arvancloudai.ir/gateway/models/Qwen3.5-35B-A3B/emVWUqJR5MMlxnzF1mUr1r46EirQWdKr326_-kjDjvMmRAOptNkVpvSdiODowQLsU_b_nIv9Y6H0S9Qa8fZaQZQSPlCPxA1Q-RZaVw2fwB8LKZbKssTDX6-2QJ9shEZL9iVLGr7ugptT_B3R_UmH3wb96SpLSb8zk9PN7wbQ9nuEyfWfOVI7PCh2VinqfP_NQ3W8IAYyGzxXdSYcGI4UN58Wws_HhgQRyVlr6Qecu2oeirrbK8Ky2waX--KM_Erf9BVpkw/v1",
        
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