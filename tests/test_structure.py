from types import SimpleNamespace
from unittest.mock import patch

from backend.structure import structure_transcript, TOOL_NAME


def _mock_tool_use_message(input_dict: dict):
    """Build a fake Anthropic Message with a single tool_use content block."""
    block = SimpleNamespace(type="tool_use", name=TOOL_NAME, input=input_dict)
    return SimpleNamespace(content=[block])


@patch("backend.structure._get_client")
def test_structure_transcript_returns_tool_input(mock_get_client):
    expected = {
        "patient_label": "Room 204",
        "shift": "Day shift",
        "vitals": {"blood_pressure": "120/80", "heart_rate": "72"},
        "subjective": "Patient reports mild headache",
        "objective": "Alert and oriented",
        "actions_taken": ["Administered 500mg Tylenol at 14:00"],
        "medications": [{"name": "Tylenol", "dose": "500mg", "time": "14:00"}],
        "assessment": "Stable",
        "plan": "Monitor and reassess in 2 hours",
        "flags": [],
    }

    mock_client = mock_get_client.return_value
    mock_client.messages.create.return_value = _mock_tool_use_message(expected)

    result = structure_transcript("patient in room 204, day shift, reports headache...")

    assert result == expected
    # confirm we forced the tool call rather than free-form text
    _, kwargs = mock_client.messages.create.call_args
    assert kwargs["tool_choice"] == {"type": "tool", "name": TOOL_NAME}


@patch("backend.structure._get_client")
def test_structure_transcript_no_tool_use_falls_back(mock_get_client):
    mock_client = mock_get_client.return_value
    mock_client.messages.create.return_value = SimpleNamespace(content=[])

    result = structure_transcript("garbled transcript")

    assert result["flags"]
