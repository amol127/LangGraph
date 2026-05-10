# LangGraph Project Notes

This project contains small examples for learning LangGraph with LLM calls.

## Files

### `chat.py`

This file shows a simple straight-line LangGraph flow.

Flow:

```text
START -> Chatbot -> samplenode -> END
```

Important parts:

- `State` defines the data that moves through the graph.
- `message` is a list of messages.
- `Annotated[list, add_messages]` tells LangGraph to append messages instead of replacing them.
- `chatbot()` sends the current messages to Groq's `llama-3.1-8b-instant` model.
- `samplenode()` appends `"Sample Message Appended"` after the chatbot response.
- `graph.invoke(...)` runs the graph once with an example message.

Environment needed:

- `.env` must contain `GROQ_API_KEY`.

### `chat2.py`

This file shows a conditional LangGraph flow.

Flow:

```text
START -> chatbot -> evaluate_response
                    -> endnode -> END
                    -> chatbot_gemini -> endnode -> END
```

Important parts:

- `State` stores:
  - `user_query`: the question from the user.
  - `llm_output`: the answer from the model.
  - `is_good`: a simple quality flag.
- `chatbot()` calls OpenRouter using the OpenAI-compatible client.
- `max_tokens=256` keeps the request small and avoids OpenRouter credit errors.
- `evaluate_response()` decides which node should run next.
- If `is_good` is true, the graph goes to `endnode`.
- If `is_good` is false, the graph goes to `chatbot_gemini` as a fallback.

Environment needed:

- `.env` must contain `OPENROUTER_API_KEY`.

Note: `chatbot_gemini` currently also uses `openai/gpt-4.1-mini`. The name says Gemini, but the model is OpenAI through OpenRouter. Rename the function or change the model later if you want a real Gemini fallback.

### `chat_checkpointing.py`

This file shows LangGraph checkpointing with MongoDB.

Flow:

```text
START -> Chatbot -> END
```

Important parts:

- `State` stores the message list.
- `chatbot()` sends the current messages to Groq.
- `MongoDBSaver` stores graph checkpoints in MongoDB.
- `graph_builder.compile(checkpointer=checkpointer)` enables checkpointing.
- `thread_id` identifies one saved conversation or graph run.
- `stream(..., stream_mode="values")` streams state updates while the graph runs.

Main idea:

```text
Checkpointing saves graph state outside Python.
```

Why it matters:

- You can continue a conversation later.
- You can inspect old state.
- You can resume long workflows.
- You can keep separate conversations using different `thread_id` values.

Example:

```python
config = {
    "configurable": {
        "thread_id": "Amol"
    }
}
```

The `thread_id` is like a save-file name.

Same `thread_id`:

```text
Use the same saved state.
```

Different `thread_id`:

```text
Create or use a different saved state.
```

Environment needed:

- `.env` must contain `GROQ_API_KEY`.
- Docker MongoDB must be running.

Run commands:

```powershell
docker compose up -d
python .\chat_checkpointing.py
```

Reset MongoDB checkpoints:

```powershell
docker compose down -v
docker compose up -d
```

### `requirements.txt`

This file lists Python packages needed by the project.

Current packages:

- `langgraph`
- `langchain`
- `langchain-community`
- `python-dotenv`
- `langchain-openai`

Note: `chat.py` imports `langchain_groq`, so the project may also need `langchain-groq` in `requirements.txt`.

### `README.md`

This is the short project readme. It currently only contains the project name.

### `.env`

This file stores private API keys. Do not commit it to GitHub.

Expected keys:

```text
GROQ_API_KEY=...
OPENROUTER_API_KEY=...
```

### `lang-graph_flow`

This file is currently empty. You can use it later for graph flow notes or diagrams.

## Quick Run Commands

Run the basic Groq graph:

```powershell
python .\chat.py
```

Run the conditional OpenRouter graph:

```powershell
python .\chat2.py
```

Run the checkpointing graph:

```powershell
docker compose up -d
python .\chat_checkpointing.py
```

## Mental Model

LangGraph works like this:

1. Define a `State`.
2. Write node functions that receive state and return updated state.
3. Add nodes to `StateGraph`.
4. Add edges to decide the path.
5. Compile the graph.
6. Invoke the graph with starting input.

With checkpointing:

1. Create a checkpointer.
2. Compile the graph with the checkpointer.
3. Run the graph with a `thread_id`.
4. LangGraph saves state in the database.
5. Use the same `thread_id` to continue that saved state later.
