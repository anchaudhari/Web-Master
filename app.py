import io
import sys
import contextlib
import streamlit as st

# Configure the Streamlit page layout to wide (ideal for IDE split screens)
st.set_page_config(
    page_title="Replit-like AI Sandbox",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 1. SIDEBAR: Authentication & API Configurations
# -----------------------------------------------------------------------------
st.sidebar.title("🤖 AI Code Assistant")
st.sidebar.markdown("Configure your free API token to power the chat assistant.")

# API Provider Selection
api_provider = st.sidebar.selectbox(
    "Choose AI Provider",
    ["Google Gemini", "Hugging Face"]
)

# Dynamic Token Inputs depending on provider
if api_provider == "Google Gemini":
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password", help="Get a free key from Google AI Studio")
    model_name = "gemini-2.5-flash" # High-speed, high-efficiency model for code generation
else:
    api_key = st.sidebar.text_input("Enter Hugging Face Token", type="password", help="Get a free User Access Token from HF settings")
    model_name = st.sidebar.selectbox(
        "Select HF Model", 
        ["Qwen/Qwen3.5-4B-Instruct", "meta-llama/Llama-3.3-70B-Instruct"]
    )

st.sidebar.markdown("---")

# Initialize Session State Variables if they don't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "editor_code" not in st.session_state:
    # Default boilerplate code for the editor
    st.session_state.editor_code = 'print("Hello from your AI Sandbox!")\n\n# Try asking the AI to write a Fibonacci function or generate data plots!'

# -----------------------------------------------------------------------------
# 2. AI Helper Functions (API Integrations)
# -----------------------------------------------------------------------------
def get_ai_response(prompt, provider, token):
    """Calls the selected free API tier to generate code / text responses."""
    system_instruction = (
        "You are an expert software engineer assistant. When asked to write code, "
        "provide a clear explanation followed by the complete Python code block enclosed in markdown ```python. "
        "Ensure the code is clean and handles basic edge cases."
    )
    
    if not token:
        return "⚠️ Please enter your API key/token in the sidebar to talk to the AI."

    try:
        if provider == "Google Gemini":
            # Using the official 2026 google-genai client structure
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=token)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                )
            )
            return response.text
            
        elif provider == "Hugging Face":
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(api_key=token)
            messages = [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
             try:
            extracted_code = ai_reply.split("```python").split("```").strip()
            st.session_state.editor_code = extracted_code
            # Utilizing serverless conversational API architecture
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=1500,
                temperature=0.2
            )
            return response.choices.message.content
            
    except Exception as e:
        return f"❌ An error occurred while communicating with the API:\n`{str(e)}`"

# -----------------------------------------------------------------------------
# 3. SIDEBAR: Chat History & Interface UI
# -----------------------------------------------------------------------------
# Render prior chat records inside the sidebar
for message in st.session_state.chat_history:
    with st.sidebar.chat_message(message["role"]):
        st.write(message["content"])

# Handle Chat inputs
if chat_input := st.sidebar.chat_input("Ask for code snippets... (e.g., 'Write a quick sort algorithm')"):
    # Render user comment
    with st.sidebar.chat_message("user"):
        st.write(chat_input)
    st.session_state.chat_history.append({"role": "user", "content": chat_input})
    
    # Generate and render AI execution content
    with st.sidebar.chat_message("assistant"):
        with st.spinner("Thinking..."):
            ai_reply = get_ai_response(chat_input, api_provider, api_key)
            st.write(ai_reply)
    st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
    
    # Optional helper: Scan and automatically pass code syntax blocks to main workspace if extracted
    if "```python" in ai_reply:
        try:
            extracted_code = ai_reply.split("```python").split("```").strip()
            st.session_state.editor_code = extracted_code
            st.rerun() # Refresh layout state to move extracted strings straight to text area
        except IndexError:
            pass


# -----------------------------------------------------------------------------
# 4. MAIN INTERFACE: Text Workspace and Virtual Compiler Environment
# -----------------------------------------------------------------------------
st.title("💻 Live Python Replit Sandbox")
st.caption("Write or generate Python code on the fly and execute it right inside your browser window context.")

# Layout workspace sections
st.subheader("Interactive Workspace")

# Code Editor Text Area synced with local session persistence state 
code_content = st.text_area(
    label="Python Code Space", 
    value=st.session_state.editor_code, 
    height=350, 
    help="Write your raw script blocks here or let the AI prompt auto-populate it.",
    key="workspace_editor"
)
# Update back into persistent tracker state
st.session_state.editor_code = code_content

col1, col2 = st.columns(2)
with col1:
    run_button = st.button("▶ Run Python Code", type="primary", use_container_width=True)
with col2:
    if st.button("Clear Canvas", type="secondary"):
        st.session_state.editor_code = ""
        st.rerun()

st.markdown("### 🖥️ Standard Console Execution Output")

# Core Compiler Emulation Engine using safe stdout intercepting 
if run_button:
    output_capture = io.StringIO()
    
    # Enclosing execution environment inside contextual capture pipelines safely
    with contextlib.redirect_stdout(output_capture), contextlib.redirect_stderr(output_capture):
        try:
            # Execute code string inside a isolated global dictionary scope context
            exec(code_content, {"__name__": "__main__"})
        except Exception as runtime_error:
            # Print error logs directly into stream context if code compile crashes
            print(f"Runtime Error: {runtime_error}", file=sys.stderr)
            
    # Capture final strings
    execution_result = output_capture.getvalue()
    
    # Show Console results output layout dynamically
    if execution_result:
        st.code(execution_result, language="shell")
    else:
        st.info("Code executed successfully with no system print output returns.")
