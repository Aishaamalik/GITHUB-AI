import streamlit as st

def troubleshooting_tab(assistant):
    st.header("🔧 Universal Git/GitHub Troubleshooting")
    st.write("Get comprehensive solutions for **any** Git or GitHub error with advanced AI-powered analysis")

    st.markdown("---")

    # Enhanced error input section
    st.subheader("📝 Error Input")
    col1, col2 = st.columns([3, 1])

    with col1:
        error_message = st.text_area(
            "Paste your Git/GitHub error message here",
            height=120,
            placeholder="Example: fatal: unable to access 'https://github.com/user/repo.git': Failed to connect to github.com port 443: Connection refused"
        )

    with col2:
        st.markdown("### Error Types We Handle:")
        st.markdown("""
        • **Network Issues** (connection, timeout)
        • **Authentication** (credentials, tokens)
        • **Repository Problems** (corruption, access)
        • **Branch Management** (detached HEAD, conflicts)
        • **GitHub API** (rate limits, permissions)
        • **Merge Conflicts** (file conflicts, overwrites)
        • **And many more...**
        """)

    if st.button("🔍 Troubleshoot Error", type="primary") and error_message:
        with st.spinner("🤖 Analyzing error and generating comprehensive solution..."):
            try:
                solution = assistant.troubleshoot_error(error_message)

                # Display results in organized sections
                st.markdown("---")
                st.markdown("## 📊 Error Analysis")

                # Error classification
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Category", solution.get('error_category', 'Unknown'))
                with col2:
                    severity_color = {
                        'Critical': '🔴',
                        'High': '🟠',
                        'Medium': '🟡',
                        'Low': '🟢'
                    }
                    severity_icon = severity_color.get(solution.get('severity', 'Medium'), '🟡')
                    st.metric("Severity", f"{severity_icon} {solution.get('severity', 'Medium')}")
                with col3:
                    st.metric("Type", solution.get('error_type', 'Unknown'))

                st.markdown("---")

                # Detailed explanation
                st.subheader("📖 Explanation")
                st.info(solution.get('explanation', 'No explanation available'))

                # Immediate actions
                st.subheader("🚀 Immediate Actions")
                immediate_actions = solution.get('immediate_actions', [])
                if immediate_actions:
                    for i, action in enumerate(immediate_actions, 1):
                        st.markdown(f"**{i}.** {action}")
                else:
                    st.warning("No immediate actions specified")

                # Detailed solution
                st.subheader("🔧 Detailed Solution")
                detailed_solution = solution.get('detailed_solution', [])
                if detailed_solution:
                    for i, step in enumerate(detailed_solution, 1):
                        st.markdown(f"**Step {i}:** {step}")
                else:
                    st.warning("No detailed solution available")

                # Commands section
                st.subheader("💻 Commands to Execute")
                commands = solution.get('commands', [])
                if commands:
                    for i, cmd in enumerate(commands, 1):
                        if cmd.startswith('#'):
                            st.markdown(f"**{cmd}**")
                        else:
                            st.code(cmd, language='bash')
                            if st.button(f"📋 Copy Command {i}", key=f"cmd_{i}"):
                                st.code(cmd, language='bash')
                                st.success(f"Command {i} copied to clipboard!")
                else:
                    st.warning("No commands provided")

                # Alternative solutions
                alternative_solutions = solution.get('alternative_solutions', [])
                if alternative_solutions:
                    st.subheader("🔄 Alternative Solutions")
                    for i, alt in enumerate(alternative_solutions, 1):
                        st.markdown(f"**Option {i}:** {alt}")

                # Verification steps
                verification_steps = solution.get('verification_steps', [])
                if verification_steps:
                    st.subheader("✅ Verification Steps")
                    for i, step in enumerate(verification_steps, 1):
                        st.markdown(f"**{i}.** {step}")

                # Prevention
                st.subheader("🛡️ Prevention")
                prevention = solution.get('prevention', 'No prevention advice available')
                st.success(prevention)

                # Additional resources
                col1, col2 = st.columns(2)

                with col1:
                    github_docs = solution.get('github_docs', '')
                    if github_docs:
                        st.markdown(f"📚 [GitHub Documentation]({github_docs})")

                with col2:
                    related_errors = solution.get('related_errors', [])
                    if related_errors:
                        st.markdown("**Related Errors:**")
                        for error in related_errors:
                            st.markdown(f"• {error}")

                # Additional resources
                additional_resources = solution.get('additional_resources', [])
                if additional_resources:
                    st.subheader("🔗 Additional Resources")
                    for resource in additional_resources:
                        st.markdown(f"• [{resource}]({resource})")

            except Exception as e:
                st.error(f"❌ Error analyzing the error message: {str(e)}")
                st.info("💡 **Tip:** Try rephrasing your error message or providing more context about when the error occurred.")
