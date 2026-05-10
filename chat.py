"""
Basic LangGraph example with a straight-line flow.

Flow:
1. Start with a list of messages.
2. Send those messages to a Groq chat model in the `chatbot` node.
3. Append one extra sample message in `samplenode`.
4. Finish and print the final state.
"""

from typing_extensions import TypedDict
from typing import Annotated
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
import os

from langchain.chat_models import init_chat_model
load_dotenv()

# Load the Groq API key from `.env` and place it into the environment.
# ChatGroq reads GROQ_API_KEY from environment variables.
os.environ["GROQ_API_KEY"] =  os.getenv("GROQ_API_KEY")
# llm = init_chat_model("groq:groq:llama-3.1-8b-instant")
from langchain_groq.chat_models import ChatGroq

# This is the LLM used by the chatbot node.
llm = ChatGroq(model="llama-3.1-8b-instant")


class State(TypedDict):
    # `add_messages` tells LangGraph to append new messages to this list
    # instead of replacing the old messages.
    message: Annotated[list, add_messages]


def chatbot(state: State):
    """Call the LLM with the current messages and return its response."""
    response = llm.invoke(state.get("message"))
    return {"message":[response]}



def samplenode(state:State):
    """Simple test node that appends one extra message after the chatbot."""
    print("\n\n\ninside sample node", state)
    return {"message":["Sample Message Appended"]}

# Create a graph that uses the `State` structure defined above.
graph_builder = StateGraph(State)

# Register functions as graph nodes.
graph_builder.add_node("Chatbot", chatbot)
graph_builder.add_node("samplenode", samplenode)

# Define the graph path:
# START -> Chatbot -> samplenode -> END
graph_builder.add_edge(START, "Chatbot" )
graph_builder.add_edge("Chatbot", "samplenode")
graph_builder.add_edge("samplenode", END)


graph = graph_builder.compile()

# Example run.
updated_state = graph.invoke(State({"message":["Hi, My name is Amol Sawant"]}))
print("\n\n\nupdated_state", updated_state)

# Explanation:

# (START) -> Chatbot -> samplenode -> (END)
# state = {message : ["hey there"]}
# node runs : Chatbot(state: ["Hey There"]) -> ["Hi, this is a message from Chatbot node"]
# state : {message : ["hey there", "Hi, this is a message from Chatbot node"]}
