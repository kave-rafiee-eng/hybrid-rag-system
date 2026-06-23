

from langchain_core.documents import Document


def markdownTextSplitter(INPUT_FILE:str)->list[Document]:
    inputText = ''
    with open( INPUT_FILE , "r" , encoding="utf-8") as f:
        inputText = f.read()

    from langchain_text_splitters import MarkdownHeaderTextSplitter

    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    chunks = splitter.split_text(inputText)
    return chunks

