"""
LangGraph checkpointing example.

Checkpointing means saving graph state outside Python while the graph runs.
Here MongoDB is used as the checkpoint database.

Flow:
1. Start with a list of messages.
2. Send those messages to a Groq chat model in the `Chatbot` node.
3. Save the graph state in MongoDB using a checkpointer.
4. Use `thread_id` as the saved conversation ID.
5. Reuse the same `thread_id` later to continue the same saved state.
"""

from typing_extensions import TypedDict
from typing import Annotated
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
import os
from langgraph.checkpoint.mongodb import MongoDBSaver
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



# Create a graph that uses the `State` structure defined above.
graph_builder = StateGraph(State)

# Register functions as graph nodes.
graph_builder.add_node("Chatbot", chatbot)


# Define the graph path:
# START -> Chatbot -> samplenode -> END
graph_builder.add_edge(START, "Chatbot" )
graph_builder.add_edge("Chatbot", END)


graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    """Compile the graph with a database-backed checkpoint saver."""
    return graph_builder.compile(checkpointer=checkpointer)
 



# Local MongoDB checkpoint database.
# Docker Compose starts MongoDB without username/password for easier practice.
MONGODB_URI = "mongodb://localhost:27017"
with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer)
    config = {
        "configurable": {
            # `thread_id` is the ID for this saved conversation.
            # Same thread_id means LangGraph can continue the same checkpoint history.
            "thread_id": "Amol"
        }
    }
    # Example run with streaming.
    # `stream_mode="values"` gives the full latest state at each step.
    for chunk in  graph_with_checkpointer.stream(
        State({"message":["what am i learning"]}),
        config,
         stream_mode="values"):
        chunk["message"][-1].pretty_print()


# Explanation:

# (START) -> Chatbot -> (END)
# state = {message : ["hey there"]}
# node runs : Chatbot(state: ["Hey There"]) -> ["Hi, this is a message from Chatbot node"]
# state : {message : ["hey there", "Hi, this is a message from Chatbot node"]}
# MongoDB saves this state using the configured thread_id.
