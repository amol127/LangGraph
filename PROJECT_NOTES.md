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

## Mental Model

LangGraph works like this:

1. Define a `State`.
2. Write node functions that receive state and return updated state.
3. Add nodes to `StateGraph`.
4. Add edges to decide the path.
5. Compile the graph.
6. Invoke the graph with starting input.

