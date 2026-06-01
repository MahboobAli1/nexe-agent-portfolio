import streamlit as st
from groq import Groq
import json
import math
import datetime
import re

st.set_page_config(page_title="Multi-Tool AI Agent | Nexe-Agent", page_icon="🛠️", layout="wide")

st.title("🛠️ Multi-Tool AI Agent")
st.caption("Task 5 — Multi-Tool AI Agent | Nexe-Agent Internship by Khadija Maqsood")

with st.sidebar:
    st.header("⚙️ Settings")
    groq_api_key = st.text_input("Groq API Key", type="password")
    st.markdown("---")
    st.subheader("🛠️ Available Tools")
    st.success("✅ Calculator")
    st.success("✅ Date & Time")
    st.success("✅ Text Analyzer")
    st.success("✅ Unit Converter")
    st.success("✅ JSON Parser")
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.agent_messages = []
        st.rerun()

# ──── Tool Definitions ────
def calculator_tool(expression: str) -> str:
    """Safe calculator"""
    try:
        allowed = re.sub(r'[^0-9+\-*/().%^ ]', '', expression)
        allowed = allowed.replace('^', '**')
        result = eval(allowed, {"__builtins__": {}, "math": math})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculator error: {str(e)}"

def datetime_tool(query: str = "") -> str:
    """Get current date/time"""
    now = datetime.datetime.now()
    return f"Current date: {now.strftime('%A, %B %d, %Y')}\nCurrent time: {now.strftime('%I:%M %p')}\nTimestamp: {now.isoformat()}"

def text_analyzer_tool(text: str) -> str:
    """Analyze text statistics"""
    words = text.split()
    sentences = text.split('.')
    chars = len(text)
    return json.dumps({
        "characters": chars,
        "words": len(words),
        "sentences": len([s for s in sentences if s.strip()]),
        "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 2),
        "unique_words": len(set(w.lower() for w in words))
    }, indent=2)

def unit_converter_tool(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between units"""
    conversions = {
        ("km", "miles"): 0.621371, ("miles", "km"): 1.60934,
        ("kg", "lbs"): 2.20462, ("lbs", "kg"): 0.453592,
        ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        ("meters", "feet"): 3.28084, ("feet", "meters"): 0.3048,
        ("liters", "gallons"): 0.264172, ("gallons", "liters"): 3.78541,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        factor = conversions[key]
        if callable(factor):
            result = factor(value)
        else:
            result = value * factor
        return f"{value} {from_unit} = {round(result, 4)} {to_unit}"
    return f"Conversion from {from_unit} to {to_unit} not supported. Supported: km/miles, kg/lbs, celsius/fahrenheit, meters/feet, liters/gallons"

def json_parser_tool(json_string: str) -> str:
    """Parse and pretty-print JSON"""
    try:
        parsed = json.loads(json_string)
        return json.dumps(parsed, indent=2)
    except Exception as e:
        return f"Invalid JSON: {str(e)}"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform mathematical calculations. Use for any math expressions.",
            "parameters": {"type": "object", "properties": {"expression": {"type": "string", "description": "Math expression e.g. '2 + 2', '15 * 7', 'sqrt(144)'"}}, "required": ["expression"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get the current date and time",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "text_analyzer",
            "description": "Analyze text to get statistics like word count, character count etc.",
            "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "unit_converter",
            "description": "Convert between units of measurement (km/miles, kg/lbs, celsius/fahrenheit, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "from_unit": {"type": "string"},
                    "to_unit": {"type": "string"}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "json_parser",
            "description": "Parse and validate JSON strings",
            "parameters": {"type": "object", "properties": {"json_string": {"type": "string"}}, "required": ["json_string"]}
        }
    }
]

def run_tool(name, args):
    if name == "calculator":
        return calculator_tool(args.get("expression", ""))
    elif name == "get_datetime":
        return datetime_tool()
    elif name == "text_analyzer":
        return text_analyzer_tool(args.get("text", ""))
    elif name == "unit_converter":
        return unit_converter_tool(args.get("value", 0), args.get("from_unit", ""), args.get("to_unit", ""))
    elif name == "json_parser":
        return json_parser_tool(args.get("json_string", ""))
    return "Tool not found"

# ──── Chat Logic ────
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

for msg in st.session_state.agent_messages:
    if msg["role"] in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

st.caption("💡 Try: 'What is 15% of 350?', 'Convert 100 km to miles', 'What time is it?', 'Analyze this text: Hello World'")

if prompt := st.chat_input("Ask me anything — I have tools!"):
    if not groq_api_key:
        st.error("Enter Groq API key in sidebar.")
        st.stop()

    st.session_state.agent_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = Groq(api_key=groq_api_key)
    with st.chat_message("assistant"):
        with st.spinner("Agent thinking..."):
            try:
                messages = [
                    {"role": "system", "content": "You are a helpful AI agent with access to tools. Use them when needed. Always show your work."},
                    *[m for m in st.session_state.agent_messages if m["role"] in ["user", "assistant"]]
                ]
                response = client.chat.completions.create(
                    model="llama3-groq-70b-8192-tool-use-preview",
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    max_tokens=1024
                )
                msg = response.choices[0].message

                # Handle tool calls
                if msg.tool_calls:
                    tool_results = []
                    for tc in msg.tool_calls:
                        tool_name = tc.function.name
                        tool_args = json.loads(tc.function.arguments)
                        with st.status(f"🛠️ Using tool: {tool_name}"):
                            result = run_tool(tool_name, tool_args)
                            st.code(result)
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result
                        })

                    # Second call with tool results
                    messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [tc.model_dump() for tc in msg.tool_calls]})
                    messages.extend(tool_results)
                    final_response = client.chat.completions.create(
                        model="llama3-groq-70b-8192-tool-use-preview",
                        messages=messages,
                        max_tokens=1024
                    )
                    final_text = final_response.choices[0].message.content
                else:
                    final_text = msg.content

                st.markdown(final_text)
                st.session_state.agent_messages.append({"role": "assistant", "content": final_text})
            except Exception as e:
                st.error(f"Error: {str(e)}")