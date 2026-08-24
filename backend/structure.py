"""
Turns a raw transcript into a structured note using the Claude API.

Rather than asking Claude to "return JSON" and hoping the formatting holds up,
this defines a tool whose input_schema is built directly from schema.json,
then forces Claude to call it (tool_choice). Claude's tool_use block is then
guaranteed to match the schema's shape — no brittle string parsing needed.

Docs: https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview

Requires ANTHROPIC_API_KEY to be set (e.g. in a .env file, or exported in
your shell). Get a key at https://console.anthropic.com — structuring a
single note costs a fraction of a cent, so even a small credit covers a lot
of testing.
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")
SCHEMA_PATH = Path(__file__).parent.parent / "schema.json"
TOOL_NAME = "record_structured_note"

SYSTEM_PROMPT = """You are a clinical documentation assistant helping a nurse turn a spoken \
shift report into a structured note. Extract only information that is actually \
present in the transcript — never infer or invent vitals, medications, or \
clinical details that weren't said. Leave a field empty (or omit it) rather \
than guessing. If something relevant seems ambiguous, contradictory, or \
missing, add a short note about it to "flags" instead of resolving it \
yourself. This is synthetic demo/portfolio data — never real patient \
information."""

_client = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    return _client


def _load_note_tool() -> dict:
    """Build an Anthropic tool definition straight from schema.json."""
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    return {
        "name": TOOL_NAME,
        "description": "Record a structured nursing shift note extracted from a transcript.",
        "input_schema": {
            "type": "object",
            "properties": schema["properties"],
            "required": schema.get("required", []),
        },
    }


def structure_transcript(transcript: str) -> dict:
    """
    Send the transcript to Claude and get back a dict matching schema.json,
    via a forced tool call so the response shape is guaranteed.
    """
    client = _get_client()
    tool = _load_note_tool()

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        tools=[tool],
        tool_choice={"type": "tool", "name": TOOL_NAME},
        messages=[
            {
                "role": "user",
                "content": f'Transcript of the shift report:\n\n"""{transcript}"""',
            }
        ],
    )

    for block in message.content:
        if block.type == "tool_use" and block.name == TOOL_NAME:
            return block.input

    # Shouldn't happen with tool_choice forcing the call, but fail safe
    # rather than crash the request.
    return {
        "vitals": {},
        "subjective": "",
        "actions_taken": [],
        "plan": "",
        "flags": ["Claude did not return a structured note — please try again."],
    }
