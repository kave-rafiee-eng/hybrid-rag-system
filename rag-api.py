from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

# from langfuse import observe
# from langfuse import Langfuse
# langfuse = Langfuse()
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.messages import HumanMessage,AIMessage

from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.graph import START,END,StateGraph
from typing import Annotated,Sequence,Literal
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel,Field
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
import os
import json

load_dotenv('.env')

#main llm
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.3,
    base_url='https://api.gapgpt.app/v1',
    api_key=os.environ["api_key"],
)

#openai Embeding
endpoint = "https://models.github.ai/inference"
model_name = "openai/text-embedding-3-small"

embeddings = OpenAIEmbeddings(
    model=model_name,
    api_key=token,
    base_url= endpoint
)

#load summarize
summarize_text = []
with open("dist/summeries.json",'r') as file:
    summarize_text = json.load(file)

#vector store   
vStore = Chroma(
    embedding_function=embeddings,
    persist_directory="./dist/db"
)

retriever = vStore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,            
        "fetch_k": 20,
        "lambda_mult": 0.5
    }
)

#BM25 Retriver
docs_summarize = [ Document(page_content=text ) for text in summarize_text ]
bm25_retriever = BM25Retriever.from_documents(docs_summarize)
bm25_retriever.k = 5

# hybrid_retriever_hd5l
hybrid_retriever_hd5l = EnsembleRetriever(
    retrievers=[retriever, bm25_retriever],
    weights=[0.6, 0.4]
)


retriver_tool_hd5l =create_retriever_tool(
    retriever = hybrid_retriever_hd5l,
    name="retriver_vector_hd5l_vfd_drive",
    description=" search in vector db and bm25_retriever about HD5L VFD AC elevator Drive"
)

tools=[retriver_tool_hd5l]

#-------------------------------------------------------- langgraph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage],add_messages]
    
def agent( state:AgentState):
    """
    Invokes the agent model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply end.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with the agent response appended to messages
    """
    messages = state['messages']
    
    llm_with_tool = llm.bind_tools(tools=tools)
    response = llm_with_tool.invoke(messages)
    
    return {"messages":[response]}

def grade_document(state:AgentState)-> Literal["generate", "rewrite"]:
    
    #print("---- GREAD DOCUMENTS CALL ---")
    class grade(BaseModel):
        binary_score : str = Field(description="Relevance score 'yes' or 'no' ")
        
    llm_with_structured_output = llm.with_structured_output(grade)
    
    prompt = PromptTemplate(
        template="""You are a grader assessing the relevance of a retrieved document to a user question.
        Here is the retrieved document:
        {context}

        Here is the user question:
        {question}

        Decide whether the document is useful for answering the question.

        The document does NOT need to directly answer the question.
        If it contains related concepts, partial information, background knowledge, or anything that could help answer the question, consider it relevant.

        Be generous in your judgment — if there is any meaningful semantic connection, mark it as relevant.

        Respond with a binary score:
        'yes' if relevant or potentially useful
        'no' if completely unrelated
        """,
        input_variables=["context", "question"],
    )

    
    chain = prompt | llm_with_structured_output
    
    messages = state['messages']
    
    lastMess = messages[-1].content
    question = messages[0].content
    
    resault = chain.invoke({"context":lastMess,"question":question})
    score = resault.binary_score

    if score == "yes":
        print("---DECISION: RELEVANT---")
        return "generate"

    else:
        print("---DECISION: DOCS NOT RELEVANT---")
        #print(score)
        return "rewrite"
    
    
def generate(state:AgentState):
    
    messages = state['messages']
    
    question = messages[0].content
    docs = messages[-1].content
    
    prompt = PromptTemplate(
        template="""
        You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        Question: {question} 
        Context: {context} 
        Answer:
        """,
        input_variables=['question','context']
    )
    
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"question":question,"context":docs})
    
    return {"messages":[response]}


def rewrite(state:AgentState):
    
    print("---TRANSFORM QUERY---")
    messages = state["messages"]
    question = messages[0].content

    prompt = PromptTemplate(
        template=""" 
        Look at the input and try to reason about the underlying semantic intent / meaning. \n 
        Here is the initial question:
        {question} 
        Formulate an improved question for search in vector dataBase(RAG) only retuen the new query
        try to be creative and new query be little diffrent to question:
        """,
        input_variables=['question']
    )
    
    chain = prompt | llm | StrOutputParser()

    help = """The previous query i created for the vector database did not return suitable results. 
    Here is a suggested query that might work better; i can use it and call my tool again whit a new query : """
    # Grader
    response = chain.invoke({'question':question})
    return {
        "messages": [
            AIMessage(content=help+response)
        ]
    }

#-----------------------------------------------------
workFlow = StateGraph(AgentState)

workFlow.add_node("agent",agent)
workFlow.add_node("retriver",ToolNode(tools=tools))
workFlow.add_node("generate",generate)
workFlow.add_node("rewrite",rewrite)

workFlow.add_edge(START,"agent")

workFlow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools":"retriver",
        END: END
    }
)

workFlow.add_conditional_edges(
    "retriver",grade_document
)

workFlow.add_edge("generate", END)
workFlow.add_edge("rewrite", "agent")

graph = workFlow.compile()

print( graph.get_graph().draw_ascii() )


for event in graph.stream(
    {"messages": "what is Slip compensation gain hd5l"},
    stream_mode="updates"
):
    print(event)
    
    
"""
project/
│
├── config/
│   └── settings.py
│
├── llm/
│   ├── llm_factory.py
│   └── embedding_factory.py
│
├── retrievers/
│   ├── vector_store.py
│   ├── bm25.py
│   └── hybrid.py
│
├── tools/
│   └── retriever_tool.py
│
├── agents/
│   ├── state.py
│   ├── nodes.py
│   └── graph_builder.py
│
└── main.py
"""