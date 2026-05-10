# LangGraph Practice

This repository contains small practice examples for learning **LangChain** and
**LangGraph**.

The goal is to understand how to call LLMs and how to control an AI workflow
using graph nodes and edges.

## Basic Idea

### LangChain

LangChain helps you work with LLMs.

Use LangChain when you want to:

- call an AI model
- send prompts or messages
- use tools
- connect memory
- parse model output

Simple flow:

```text
User input -> LLM -> Response
```

In this project, `chat.py` uses LangChain/Groq here:

```python
llm = ChatGroq(model="llama-3.1-8b-instant")
response = llm.invoke(state.get("message"))
```

### LangGraph

LangGraph helps you control the workflow.

Use LangGraph when you want to:

- create steps as nodes
- connect nodes with edges
- branch based on conditions
- keep state between steps
- build agent-like flows

Simple flow:

```text
START -> Node 1 -> Node 2 -> END
```

In this project, `chat.py` creates this graph:

```text
START -> Chatbot -> samplenode -> END
```

## LangChain vs LangGraph

Easy memory:

```text
LangChain = call and use the AI model
LangGraph = control the AI workflow
```

Another way:

```text
LangChain is the engine.
LangGraph is the road map.
```

## Project Files

### `chat.py`

Basic LangGraph example with a straight-line flow.

Flow:

```text
START -> Chatbot -> samplenode -> END
```

What it does:

- loads `GROQ_API_KEY` from `.env`
- creates a Groq chat model
- sends a message to the model
- appends one sample message
- prints the final graph state

### `chat2.py`

Conditional LangGraph example.

Flow:

```text
START -> chatbot -> evaluate_response -> endnode -> END
```

If the first response is not good, it can go to a fallback node:

```text
chatbot -> chatbot_gemini -> endnode -> END
```

What it does:

- loads `OPENROUTER_API_KEY` from `.env`
- calls OpenRouter using the OpenAI-compatible client
- stores the LLM answer in graph state
- checks if the answer is non-empty
- decides the next graph node based on that check

### `chat_checkpointing.py`

LangGraph checkpointing example.

Flow:

```text
START -> Chatbot -> END
```

What it does:

- loads `GROQ_API_KEY` from `.env`
- creates a Groq chat model
- creates a MongoDB checkpointer
- compiles the graph with that checkpointer
- runs the graph using a `thread_id`
- saves the conversation state in MongoDB

The important new topic here is **checkpointing**.

## Checkpointing

Checkpointing means saving the graph state while the graph runs.

Without checkpointing:

```text
Run graph -> get final answer -> state disappears after program ends
```

With checkpointing:

```text
Run graph -> save state -> continue later using same thread_id
```

In simple words:

```text
Checkpointing = memory saved outside Python
```

In this project, MongoDB stores the checkpoints.

### Why Checkpointing Is Useful

Checkpointing is useful when you want:

- chat history to continue later
- long-running workflows
- pause and resume
- debugging old graph runs
- human approval steps
- agents that remember previous state

### Important Code

The checkpointer is created here:

```python
MONGODB_URI = "mongodb://localhost:27017"

with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer)
```

The graph is compiled with checkpointing here:

```python
def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)
```

The `thread_id` is very important:

```python
config = {
    "configurable": {
        "thread_id": "Amol"
    }
}
```

Think of `thread_id` as the conversation ID.

Same `thread_id` means:

```text
Continue the same saved conversation
```

Different `thread_id` means:

```text
Start a different saved conversation
```

### MongoDB For Checkpoints

This project uses Docker MongoDB.

Start MongoDB:

```powershell
docker compose up -d
```

Stop MongoDB:

```powershell
docker compose down
```

Reset MongoDB data:

```powershell
docker compose down -v
docker compose up -d
```

Use reset only when you want to delete old saved checkpoints.

### `PROJECT_NOTES.md`

Extra notes explaining the files and the mental model of the project.

### `lang-graph_flow`

Empty file for writing flow notes or diagrams later.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file:

```text
GROQ_API_KEY=your_groq_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

Do not upload `.env` to GitHub because it contains private API keys.

## Run

Run the basic Groq example:

```powershell
python .\chat.py
```

Run the conditional OpenRouter example:

```powershell
python .\chat2.py
```

Run the MongoDB checkpointing example:

```powershell
docker compose up -d
python .\chat_checkpointing.py
```

## Important LangGraph Words

### State

State is the data that moves through the graph.

Example:

```python
class State(TypedDict):
    message: Annotated[list, add_messages]
```

### Node

A node is a function that does one step of work.

Example:

```python
def chatbot(state: State):
    response = llm.invoke(state.get("message"))
    return {"message": [response]}
```

### Edge

An edge connects one node to another node.

Example:

```python
graph_builder.add_edge(START, "Chatbot")
graph_builder.add_edge("Chatbot", "samplenode")
graph_builder.add_edge("samplenode", END)
```

### Conditional Edge

A conditional edge chooses the next node based on logic.

Example from `chat2.py`:

```python
graph_builder.add_conditional_edges("chatbot", evaluate_response)
```

## Learning Order

Recommended order:

1. Read `README.md`.
2. Read `chat.py`.
3. Run `chat.py`.
4. Read `chat2.py`.
5. Run `chat2.py`.
6. Read `PROJECT_NOTES.md`.

## Quick Mental Model

Every LangGraph app follows this pattern:

```text
Define State
Write node functions
Add nodes
Add edges
Compile graph
Invoke graph
```

With checkpointing, add one more idea:

```text
Compile graph with checkpointer
Run graph with thread_id
State gets saved in database
Later use same thread_id to continue
```
