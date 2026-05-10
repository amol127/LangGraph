"""
Simple conditional LangGraph example.

Flow:
1. Take a user question.
2. Send it to an LLM in the `chatbot` node.
3. Check if the LLM gave a non-empty answer.
4. If the answer is good, finish the graph.
5. If the answer is not good, try the fallback chatbot node.
"""

from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Optional, Literal
from langgraph.graph import StateGraph, START, END
# from langchain_openai import OpenAI
from openai import OpenAI
import os

load_dotenv()

# OpenRouter uses the OpenAI-compatible client.
# The actual key is stored in `.env` as OPENROUTER_API_KEY.
api_key = os.getenv("OPENROUTER_API_KEY")
client  = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
    
)

class State(TypedDict):
    # Data that travels through every node in the graph.
    user_query : str
    llm_output : Optional[str]
    is_good: Optional[bool]


def chatbot(state: State):
    """Main LLM node: answer the user's query."""
    print("\n\n\nInside the chatBot clling")
    response = client.chat.completions.create(
        model="openai/gpt-4.1-mini",
        # Keep token usage small so OpenRouter does not reserve a huge budget.
        max_tokens=256,
        messages=[
            {"role":"user", "content":state.get("user_query")}
        ]
    )

    # Save the model answer back into graph state.
    state["llm_output"] = response.choices[0].message.content

    # Very simple quality check: any non-empty response is considered good.
    state["is_good"] = bool(state["llm_output"])
    return state


def evaluate_response(state: State) -> Literal["chatbot_gemini", "endnode"]:
    """Choose the next node based on whether the first answer was good."""
    if state.get("is_good"):
        return "endnode"
    else:
        return "chatbot_gemini"

def endnode(state: State):
    """Final node: return the completed state unchanged."""
    return state


def chatbot_gemini(state:State):
    """Fallback LLM node used when the first answer is not good."""
    print("\n\n\nInside the Gemini clling")
    response = client.chat.completions.create(
        model="openai/gpt-4.1-mini",
        max_tokens=256,
        messages=[
            {"role":"user", "content":state.get("user_query")}
        ]
    )

    state["llm_output"] = response.choices[0].message.content
    state["is_good"] = bool(state["llm_output"])
    return state



# Build the LangGraph.
graph_builder = StateGraph(State)

# Register each Python function as a graph node.
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("chatbot_gemini", chatbot_gemini)
graph_builder.add_node("endnode", endnode)

# Define how execution moves between nodes.
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", evaluate_response)
graph_builder.add_edge("chatbot_gemini", "endnode")
graph_builder.add_edge("endnode", END)


graph = graph_builder.compile()

# Example run.
update_response = graph.invoke(State({"user_query":"Hey, What is 2+2 ?"}))
print("update_response: ",update_response)




