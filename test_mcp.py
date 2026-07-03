"""Test MCP server with full workflow."""

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

def main():
    # Initialize
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
    ]

    # Create session
    messages.append({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "create_session", "arguments": {}}})

    responses = send_mcp(messages)
    session_id = json.loads(responses[-1]["result"]["content"][0]["text"])["session_id"]
    print(f"[OK] Created session: {session_id}")

    # Add slide
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "add_slide", "arguments": {"session_id": session_id, "bg_type": "solid", "color": "#FFFFFF"}}},
    ]
    responses = send_mcp(messages)
    print(f"[OK] Added slide")

    # Add textbox
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "add_textbox", "arguments": {
            "session_id": session_id,
            "slide_index": 0,
            "x": 100, "y": 100, "w": 800, "h": 100,
            "text": "Hello DrawPPT!\nThis is a test.",
            "font_size": 36,
            "bold": True,
            "color": "#333333"
        }}},
    ]
    responses = send_mcp(messages)
    result = json.loads(responses[-1]["result"]["content"][0]["text"])
    print(f"[OK] Added textbox: {result['element_id']}")

    # Add shape
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "add_shape", "arguments": {
            "session_id": session_id,
            "slide_index": 0,
            "x": 100, "y": 300, "w": 400, "h": 300,
            "shape_type": "rounded_rectangle",
            "fill_color": "#4A90D9"
        }}},
    ]
    responses = send_mcp(messages)
    result = json.loads(responses[-1]["result"]["content"][0]["text"])
    print(f"[OK] Added shape: {result['element_id']}")

    # Preview
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "preview_slides", "arguments": {"session_id": session_id}}},
    ]
    responses = send_mcp(messages)
    preview = json.loads(responses[-1]["result"]["content"][0]["text"])
    print(f"\n[OK] Preview:")
    print(json.dumps(preview, indent=2, ensure_ascii=False))

    # Export
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "export_pptx", "arguments": {"session_id": session_id, "output_path": "test_mcp_output.pptx"}}},
    ]
    responses = send_mcp(messages)
    result = json.loads(responses[-1]["result"]["content"][0]["text"])
    print(f"\n[OK] Exported: {result['file_path']}")

    print("\n[DONE] All tests passed!")

if __name__ == "__main__":
    main()
