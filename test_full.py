"""Full MCP workflow test."""

import json
import subprocess

def send_mcp(input_text):
    """Send MCP messages and get responses."""
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

# Build all messages
messages = []
msg_id = 1

def add_tool_call(name, args):
    global msg_id
    messages.append({"jsonrpc": "2.0", "id": msg_id, "method": "tools/call", "params": {"name": name, "arguments": args}})
    msg_id += 1

# Initialize
messages.append({"jsonrpc": "2.0", "id": msg_id, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}})
msg_id += 1
messages.append({"jsonrpc": "2.0", "method": "notifications/initialized"})

# Create session
add_tool_call("create_session", {})

# Add slide
add_tool_call("add_slide", {"session_id": "{{SESSION_ID}}", "bg_type": "solid", "color": "#FFFFFF"})

# Add textbox
add_tool_call("add_textbox", {"session_id": "{{SESSION_ID}}", "slide_index": 0, "x": 100, "y": 100, "w": 800, "h": 100, "text": "Hello DrawPPT!\nThis is a test.", "font_size": 36, "bold": True, "color": "#333333"})

# Add shape
add_tool_call("add_shape", {"session_id": "{{SESSION_ID}}", "slide_index": 0, "x": 100, "y": 300, "w": 400, "h": 300, "shape_type": "rounded_rectangle", "fill_color": "#4A90D9"})

# Preview
add_tool_call("preview_slides", {"session_id": "{{SESSION_ID}}"})

# Export
add_tool_call("export_pptx", {"session_id": "{{SESSION_ID}}", "output_path": "test_full_output.pptx"})

# First pass: get session_id
input_text = "\n".join(json.dumps(m) for m in messages[:3])  # init + create_session
responses = send_mcp(input_text)

session_id = None
for r in responses:
    if "result" in r and "content" in r.get("result", {}):
        content = r["result"]["content"][0]["text"]
        try:
            data = json.loads(content)
            if "session_id" in data:
                session_id = data["session_id"]
                print(f"[OK] Session: {session_id}")
        except:
            pass

if not session_id:
    print("[ERROR] Failed to create session")
    exit(1)

# Second pass: use session_id for remaining calls
remaining = messages[3:]  # Skip init + create_session
for m in remaining:
    # Replace placeholder
    m_str = json.dumps(m).replace("{{SESSION_ID}}", session_id)
    m = json.loads(m_str)

# Build full input with session_id
full_input = []
for m in messages:
    m_str = json.dumps(m).replace("{{SESSION_ID}}", session_id)
    full_input.append(m_str)

responses = send_mcp("\n".join(full_input))

# Parse responses
for i, r in enumerate(responses):
    if "id" not in r:
        continue
    if "result" in r and "content" in r.get("result", {}):
        content = r["result"]["content"][0]["text"]
        try:
            data = json.loads(content)
            if "session_id" in data and "slide_count" in data:
                print(f"[OK] Slide added")
            elif "element_id" in data:
                if "shape_type" in data:
                    print(f"[OK] Shape added: {data['element_id']}")
                else:
                    print(f"[OK] Textbox added: {data['element_id']}")
            elif "slides" in data:
                print(f"[OK] Preview: {len(data['slides'])} slides")
            elif "file_path" in data:
                print(f"\n[OK] Exported: {data['file_path']}")
        except:
            pass

print("\n[DONE] Test complete!")
