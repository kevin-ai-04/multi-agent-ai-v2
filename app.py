import streamlit as st
from backend.graph import app as workflow

# Page Configuration
st.set_page_config(
    page_title="Multi-Agent Procurement System",
    page_icon="🤖",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.header("System Control")
    
    col1, col2 = st.columns(2)
    with col1:
        agent_a_enabled = st.toggle("Enable Agent A (Num2Text)", value=True)
    with col2:
        agent_b_enabled = st.toggle("Enable Agent B (Text2Num)", value=True)
    
    st.divider()
    
    st.subheader("System Status")
    if agent_a_enabled and agent_b_enabled:
        st.success("System Online: All Agents Active")
    elif not agent_a_enabled and not agent_b_enabled:
        st.error("System Offline: All Agents Disabled")
    else:
        st.warning("System Degraded: Some Agents Disabled")

# Main Interface
st.title("🤖 Multi-Agent Procurement System")
st.markdown("""
This system uses a central **Orchestrator** to route your input to the appropriate specialist agent:
- **Agent A (Num2Text)**: Converts digits to text (e.g., 42 -> forty-two)
- **Agent B (Text2Num)**: Converts text to digits (e.g., one hundred -> 100)
""")

# Chat History initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "steps" in message:
            with st.expander("Show Internal Thought Process"):
                for step in message["steps"]:
                    st.markdown(f"- {step}")

# Chat Input
if prompt := st.chat_input("Enter a number or text to convert..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Invoke Graph
    with st.chat_message("assistant"):
        with st.status("Orchestrator Processing...", expanded=True) as status:
            st.write("Analyzing input...")
            
            # Prepare inputs
            inputs = {
                "input_text": prompt,
                "agent_a_enabled": agent_a_enabled,
                "agent_b_enabled": agent_b_enabled
            }
            
            # Run graph
            # Run graph
            response_text = None
            steps = []
            
            try:
                result = workflow.invoke(inputs)
                
                # Extract results
                response_text = result.get("output_text", "Error processing request.")
                steps = result.get("steps", [])
                
                # Update status
                for step in steps:
                    st.write(step)
                status.update(label="Processing Complete", state="complete", expanded=False)
                
            except Exception as e:
                status.update(label="Error Occurred", state="error")
                st.error(f"An error occurred: {str(e)}")
        
        # Display result outside the status container
        if response_text:
            st.markdown(response_text)
            
            # Add assistant message to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text,
                "steps": steps
            })
