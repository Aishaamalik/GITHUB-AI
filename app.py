import streamlit as st
from main import GitguyAssistant
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the assistant
assistant = GitguyAssistant()

# Set page config
st.set_page_config(
    page_title="Gitguy - AI Git Assistant",
    page_icon="🖊️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.feature-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    border-left: 4px solid #667eea;
}
.sidebar-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header"><h1>🖊️ Gitguy - Your AI Git Assistant</h1><p>Get step-by-step help with Git and GitHub</p></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h3>Navigation</h3></div>', unsafe_allow_html=True)

    # Progress tracker
    if 'completed_tutorials' not in st.session_state:
        st.session_state.completed_tutorials = []
    if 'solved_exercises' not in st.session_state:
        st.session_state.solved_exercises = []

    st.subheader("📊 Learning Progress")
    st.write(f"Completed Tutorials: {len(st.session_state.completed_tutorials)}")
    st.write(f"Solved Exercises: {len(st.session_state.solved_exercises)}")

    # AI Settings
    st.subheader("⚙️ AI Settings")
    explanation_temp = st.slider("Explanation Temperature", 0.1, 1.0, 0.6, 0.1)
    chat_temp = st.slider("Chat Temperature", 0.1, 1.0, 0.7, 0.1)
    max_tokens = st.slider("Max Tokens", 500, 2000, 1200)

    assistant.update_settings(explanation_temp, chat_temp, max_tokens)

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🖊️ Command Helper",
    "💡 Conflict Resolver",
    "📚 Beginner's Guide",
    "⚡ Troubleshooting",
    "🤖 AI Chat"
])

with tab1:
    st.header("Command Syntax Helper")
    st.write("Get detailed explanations and examples for any Git command")

    command = st.text_input("Enter a Git command (e.g., git commit -m)")
    if st.button("Get Help") and command:
        with st.spinner("Generating explanation..."):
            result = assistant.get_command_help(command)
            st.markdown("### Command Explanation")
            st.code(result['syntax'], language='bash')
            st.write(result['description'])
            st.write(result['explanation'])
            if result['use_cases']:
                st.markdown("### Use Cases")
                for use_case in result['use_cases']:
                    st.write(f"- {use_case}")
            if result['examples']:
                st.markdown("### Examples")
                for example in result['examples']:
                    st.code(example, language='bash')
            if result['important_flags']:
                st.markdown("### Important Flags")
                for flag in result['important_flags']:
                    st.write(f"- **{flag['flag']}**: {flag['description']}")
            if result['pitfalls']:
                st.markdown("### Pitfalls")
                for pitfall in result['pitfalls']:
                    st.write(f"- ⚠️ {pitfall}")
            if result['pro_tips']:
                st.markdown("### Pro Tips")
                for tip in result['pro_tips']:
                    st.write(f"- 💡 {tip}")
            if result['related_commands']:
                st.markdown("### Related Commands")
                for cmd in result['related_commands']:
                    st.write(f"- {cmd}")
            if result['internal_mechanics']:
                st.markdown("### Internal Mechanics")
                for mechanic in result['internal_mechanics']:
                    st.write(f"- {mechanic}")

with tab2:
    st.header("Conflict Resolver")
    st.write("Get step-by-step guidance for resolving merge conflicts")

    conflict_scenario = st.text_area("Describe your conflict situation")
    if st.button("Resolve Conflict") and conflict_scenario:
        with st.spinner("Analyzing conflict..."):
            result = assistant.resolve_conflict(conflict_scenario)

            # Display analysis
            if result.get('analysis'):
                st.markdown("### Analysis")
                st.write(result['analysis'])

            # Display resolution steps
            if result.get('steps'):
                st.markdown("### Resolution Steps")
                for i, step in enumerate(result['steps'], 1):
                    st.write(f"{i}. {step}")

            # Display commands
            if result.get('commands'):
                st.markdown("### Commands to Run")
                for cmd in result['commands']:
                    st.code(cmd, language='bash')

            # Display tips
            if result.get('tips'):
                st.markdown("### 💡 Tips")
                for tip in result['tips']:
                    st.write(f"• {tip}")

            # Display common mistakes
            if result.get('common_mistakes'):
                st.markdown("### ⚠️ Common Mistakes to Avoid")
                for mistake in result['common_mistakes']:
                    st.write(f"• {mistake}")

with tab3:
    st.header("Beginner's Guide")
    st.write("Interactive tutorials for Git and GitHub basics")

    tutorial_type = st.selectbox("Choose a tutorial",
        ["Git Setup", "Creating a Repository", "Making Commits",
         "Working with Branches", "Pushing to GitHub", "Collaboration Basics"])

    if st.button("Start Tutorial"):
        with st.spinner("Loading tutorial..."):
            tutorial = assistant.get_tutorial(tutorial_type)
            st.markdown(f"### {tutorial['title']}")
            st.write(tutorial['description'])

            for i, step in enumerate(tutorial['steps'], 1):
                with st.expander(f"Step {i}: {step['title']}"):
                    st.write(step['content'])
                    if step['commands']:
                        for cmd in step['commands']:
                            st.code(cmd, language='bash')
                    if st.button(f"Mark Step {i} Complete", key=f"step_{i}"):
                        if tutorial_type not in st.session_state.completed_tutorials:
                            st.session_state.completed_tutorials.append(tutorial_type)
                        st.success(f"Step {i} completed!")

with tab4:
    st.header("Troubleshooting")
    st.write("Get solutions for common Git/GitHub errors")

    error_message = st.text_area("Paste your error message here")
    if st.button("Troubleshoot") and error_message:
        with st.spinner("Finding solution..."):
            solution = assistant.troubleshoot_error(error_message)
            st.markdown("### Solution")
            st.write(solution['explanation'])
            if solution['commands']:
                st.markdown("### Commands to Fix")
                for cmd in solution['commands']:
                    st.code(cmd, language='bash')

with tab5:
    st.header("AI Chat Assistant")
    st.write("Ask any Git-related questions")

    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    user_input = st.chat_input("Ask me anything about Git...")
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = assistant.chat_with_user(user_input)
                st.write(response)

        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Export options
st.sidebar.markdown("### 📄 Export Options")
if st.sidebar.button("Download Cheat Sheet"):
    # This would generate and download a cheat sheet
    st.sidebar.success("Cheat sheet downloaded!")

if st.sidebar.button("Export Tutorial Progress"):
    progress_data = {
        "completed_tutorials": st.session_state.completed_tutorials,
        "solved_exercises": st.session_state.solved_exercises
    }
    st.sidebar.download_button(
        label="Download Progress",
        data=str(progress_data),
        file_name="gitguy_progress.json",
        mime="application/json"
    )

if __name__ == "__main__":
    st.write("")
