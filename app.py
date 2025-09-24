import streamlit as st
from main import GitguyAssistant
import os
from dotenv import load_dotenv
from troubleshooting import troubleshooting_tab

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

# Enhanced GitHub-inspired CSS
st.markdown("""
<style>
/* Import GitHub fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Dark theme variables */
:root {
    --github-dark-bg: #0d1117;
    --github-dark-secondary: #161b22;
    --github-dark-tertiary: #21262d;
    --github-dark-accent: #30363d;
    --github-border: #30363d;
    --github-text-primary: #f0f6fc;
    --github-text-secondary: #8b949e;
    --github-text-muted: #6e7681;
    --github-blue: #238636;
    --github-blue-hover: #2ea043;
    --github-green: #238636;
    --github-purple: #8b5cf6;
    --github-orange: #f85149;
    --github-yellow: #f2cc60;
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
    --shadow-hover: 0 4px 6px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.12);
}

/* Global styles */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body {
    background-color: var(--github-dark-bg);
    color: var(--github-text-primary);
}

/* Main header */
.main-header {
    background: linear-gradient(135deg, var(--github-dark-secondary) 0%, var(--github-dark-tertiary) 100%);
    color: var(--github-text-primary);
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    border: 1px solid var(--github-border);
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g fill="%23f0f6fc" fill-opacity="0.03"><circle cx="30" cy="30" r="2"/></g></svg>');
    opacity: 0.5;
}

.main-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(135deg, var(--github-text-primary), var(--github-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
    z-index: 1;
}

.main-header p {
    font-size: 1.1rem;
    color: var(--github-text-secondary);
    margin: 0.5rem 0 0 0;
    position: relative;
    z-index: 1;
}

/* Feature cards */
.feature-card {
    background: var(--github-dark-secondary);
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border: 1px solid var(--github-border);
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
    border-color: var(--github-blue);
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, var(--github-blue), var(--github-purple));
}

/* Sidebar header */
.sidebar-header {
    background: var(--github-dark-tertiary);
    color: var(--github-text-primary);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border: 1px solid var(--github-border);
    box-shadow: var(--shadow);
}

/* Streamlit components styling */
.stTabs [data-baseweb="tab-list"] {
    background: var(--github-dark-secondary);
    border-radius: 8px;
    padding: 0.5rem;
    border: 1px solid var(--github-border);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--github-text-secondary);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--github-dark-accent);
    color: var(--github-text-primary);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--github-blue);
    color: white;
}

/* Buttons */
.stButton button {
    background: var(--github-blue);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: var(--shadow);
}

.stButton button:hover {
    background: var(--github-blue-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-hover);
}

/* Input fields */
.stTextInput input, .stTextArea textarea {
    background: var(--github-dark-secondary);
    color: var(--github-text-primary);
    border: 1px solid var(--github-border);
    border-radius: 8px;
    padding: 0.75rem;
    transition: all 0.2s ease;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--github-blue);
    box-shadow: 0 0 0 3px rgba(35, 134, 54, 0.1);
}

/* Code blocks */
.stCodeBlock {
    background: var(--github-dark-tertiary);
    border: 1px solid var(--github-border);
    border-radius: 8px;
    box-shadow: var(--shadow);
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--github-dark-secondary);
    border: 1px solid var(--github-border);
    border-radius: 8px;
    color: var(--github-text-primary);
}

.streamlit-expanderContent {
    background: var(--github-dark-tertiary);
    border: 1px solid var(--github-border);
    border-top: none;
    border-radius: 0 0 8px 8px;
}

/* Metrics */
.stMetric {
    background: var(--github-dark-secondary);
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid var(--github-border);
    box-shadow: var(--shadow);
}

/* Progress indicators */
.stProgress > div > div {
    background: var(--github-blue);
}

/* Select boxes */
.stSelectbox select {
    background: var(--github-dark-secondary);
    color: var(--github-text-primary);
    border: 1px solid var(--github-border);
    border-radius: 8px;
}

/* Chat messages */
.stChatMessage {
    background: var(--github-dark-secondary);
    border: 1px solid var(--github-border);
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: var(--shadow);
}

/* Success/Error messages */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 8px;
    padding: 1rem;
    border-left: 4px solid;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.stMarkdown {
    animation: fadeIn 0.5s ease-out;
}

/* Responsive design */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 2rem;
    }

    .feature-card {
        padding: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 0.75rem;
        font-size: 0.9rem;
    }
}

/* Loading spinner */
.stSpinner {
    color: var(--github-blue);
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--github-dark-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--github-dark-accent);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--github-blue);
}
</style>
""", unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h2>🖊️ Gitguy</h2><p>Your AI Git Assistant</p></div>', unsafe_allow_html=True)

    st.markdown("### 🚀 Quick Actions")
    if st.button("📋 Get Command Help", use_container_width=True):
        st.session_state.active_tab = "Command Helper"
    if st.button("🔧 Resolve Conflicts", use_container_width=True):
        st.session_state.active_tab = "Conflict Resolver"
    if st.button("📚 Learn Git", use_container_width=True):
        st.session_state.active_tab = "Beginner's Guide"
    if st.button("⚡ Troubleshoot", use_container_width=True):
        st.session_state.active_tab = "Troubleshooting"
    if st.button("🤖 Chat with AI", use_container_width=True):
        st.session_state.active_tab = "AI Chat"

    st.markdown("---")
    st.markdown("### 🔗 Useful Links")
    st.markdown("""
    • [Git Documentation](https://git-scm.com/doc)
    • [GitHub Docs](https://docs.github.com)
    • [GitHub Community](https://github.community)
    • [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
    • [Interactive Git Tutorial](https://learngitbranching.js.org/)
    """)

    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.info("💡 Use the search feature in tutorials to find specific topics!")
    st.info("💡 Copy commands directly from the code blocks for easy use!")

    st.markdown("---")
    st.markdown("### 📊 App Info")
    st.caption("Built with Streamlit, LangChain, and Groq AI")
    st.caption("Version 1.0.0")

# Main header
st.markdown('<div class="main-header"><h1>🖊️ Gitguy - Your AI Git Assistant</h1><p>Get step-by-step help with Git and GitHub</p></div>', unsafe_allow_html=True)



# Main content tabs with enhanced styling
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

    # Search functionality
    st.subheader("🔍 Search Any GitHub Topic")
    search_topic = st.text_input("Enter any GitHub-related topic (e.g., 'pull requests', 'GitHub Actions', 'forking')")

    if st.button("Search Tutorial") and search_topic:
        with st.spinner("Generating tutorial..."):
            tutorial = assistant.search_tutorial(search_topic.strip())
            st.markdown(f"### {tutorial['title']}")
            st.write(tutorial['description'])

            # Prerequisites
            if tutorial['prerequisites']:
                st.markdown("### Prerequisites")
                for prereq in tutorial['prerequisites']:
                    st.write(f"• {prereq}")

            # Steps
            for i, step in enumerate(tutorial['steps'], 1):
                with st.expander(f"Step {i}: {step['title']}"):
                    st.write(step['content'])
                    if step['commands']:
                        for cmd in step['commands']:
                            st.code(cmd, language='bash')
                    if step['tips']:
                        st.markdown("**Tips:**")
                        for tip in step['tips']:
                            st.write(f"• {tip}")

            # Summary
            st.markdown("### Summary")
            st.write(tutorial['summary'])

            # Next steps
            if tutorial['next_steps']:
                st.markdown("### Next Steps")
                for next_step in tutorial['next_steps']:
                    st.write(f"• {next_step}")

    st.markdown("---")

    # Original predefined tutorials
    st.subheader("📚 Predefined Tutorials")
    tutorial_type = st.selectbox("Or choose from popular tutorials:",
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

with tab4:
    troubleshooting_tab(assistant)

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



if __name__ == "__main__":
    st.write("")
