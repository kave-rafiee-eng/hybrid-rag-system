import json

def jsonFileToDocuments(INPUT_FILE:str):
    inputJson = []
    with open( INPUT_FILE , "r" , encoding="utf-8") as f:
        inputJson = json.load(f)

    from langchain_core.documents import Document

    chunks = [
        Document(page_content=json.dumps(menu, ensure_ascii=False)) 
        for menu in inputJson
    ]

    return chunks