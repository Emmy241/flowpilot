import json
from openai import OpenAI
from app.config import settings

client = OpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
)

MODEL = "openai/gpt-4o"

SYSTEM_PROMPT = """You are FlowPilot, an assistant that turns user requests into structured tasks.

Rules:
- If the user expresses a clear intent to remember, do, schedule, or track something, call the `create_task` tool immediately. Do NOT ask for confirmation — the user will approve or reject the action in the UI.
- If the user is just chatting or asking a general question, respond normally with text and do not call any tool.
- Never say "shall I go ahead" or "I can help you create". Either call the tool, or answer the question.

Be concise."""

TOOLS = [{
    "type": "function",
    "function": {
        "name": "create_task",
        "description": (
            "Create a task. Call this whenever the user mentions something "
            "they want to remember, do, or track. Do not ask for confirmation first."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short task title"},
                "description": {"type": "string", "description": "Optional details"},
            },
            "required": ["title"],
        },
    },
}]


def run_llm(messages: list[dict], tools: list | None = None) -> dict:
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    resp = client.chat.completions.create(
        model=MODEL,
        messages=full_messages,
        tools=tools or TOOLS,
        tool_choice="auto",
        max_tokens=500,
    )
    msg = resp.choices[0].message

    raw_calls = None
    normalized_calls = None

    if msg.tool_calls:
        raw_calls = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ]
        normalized_calls = [
            {
                "id": tc.id,
                "name": tc.function.name,
                "args": json.loads(tc.function.arguments),
            }
            for tc in msg.tool_calls
        ]

    return {
        "content": msg.content,
        "tool_calls": normalized_calls,   # for your app logic
        "raw_tool_calls": raw_calls,      # for storage & replay to the API
    }
