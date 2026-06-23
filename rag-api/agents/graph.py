# agents/nodes.py
from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from typing import Annotated, Sequence,Literal
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel,Field

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
                            
class AgenticRag:

    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools

    #------------------------------------------
    def agent(self, state : AgentState ):
        llm_with_tool = self.llm.bind_tools(tools=self.tools)
        response = llm_with_tool.invoke(state["messages"])
        return {"messages": [response]}

    #------------------------------------------
    def grade_document(self , state:AgentState)-> Literal["generate", "rewrite"]:

        class grade(BaseModel):
            binary_score : str = Field(description="Relevance score 'yes' or 'no' ")
            
        llm_with_structured_output = self.llm.with_structured_output(grade)
        
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
            return "rewrite"


    def generate(self, state : AgentState ):
        messages = state["messages"]
        
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
        
        chain = prompt | self.llm | StrOutputParser()
        
        response = chain.invoke({"question":question,"context":docs})
        
        return {"messages":[AIMessage(response)]}

    def rewrite(self , state:AgentState):
        
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
        
        chain = prompt | self.llm | StrOutputParser()

        help = """The previous query i created for the vector database did not return suitable results. 
        Here is a suggested query that might work better; i can use it and call my tool again whit a new query : """
        # Grader
        response = chain.invoke({'question':question})
        return {
            "messages": [
                AIMessage(content=help+response)
            ]
        }

  
    def build(self):
        workFlow = StateGraph( AgentState )

        workFlow.add_node("agent",self.agent)
        workFlow.add_node("toolsNode",ToolNode(tools= self.tools ))
        workFlow.add_node("generate", self.generate )
        workFlow.add_node("rewrite", self.rewrite )

        workFlow.add_edge(START, "agent")

        workFlow.add_conditional_edges(
            "agent",
            tools_condition,
            {
                "tools": "toolsNode",
                END: END
            }
        )


        workFlow.add_conditional_edges(
            "toolsNode", self.grade_document
        )

        workFlow.add_edge("generate", END)
        workFlow.add_edge("rewrite", "agent")

        return workFlow.compile()