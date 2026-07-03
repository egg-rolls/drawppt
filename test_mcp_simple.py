"""Simple MCP test."""

import json
import subprocess

def send_mcp(messages):
    """Send MCP messages and get responses."""
    input_text = "\n".join(json.dumps(m) for m in messages)
    result = subprocess.run(
        ["drawppt"],
        input=input_text,
        capture_output=True,
        text=True,
        timeout=30
    )
    responses = []
    for line in result.stdout.strip().split("\n"):
        try:
            responses.append(json.loads(line))
        except:
            pass
    return responses

# Initialize + create session
messages = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "create_session", "arguments": {}}},
]

responses = send_mcp(messages)
print(f"Responses: {len(responses)}")
for i, r in enumerate(responses):
    print(f"\n--- Response {i} ---")
    print(json.dumps(r, indent=2, ensure_ascii=False))
